"""
yaw_optimization.py

Standalone wake-steering optimization script for final saved layouts.

Workflow:
1) Load site and model configuration like slsqp_optimization.py.
2) Load the highest-PI saved layout for the configured site.
3) Optimize yaw angles at the most common wind speed across all wind directions.
4) Apply a rule-based yaw schedule over the full PI wind rose.
5) Evaluate AEP/economics uplift and save annotated wake maps.
"""

import csv
import json
import os
import time
import traceback

import matplotlib.pyplot as plt
import numpy as np

from floris import FlorisModel, TimeSeries
from floris.flow_visualization import visualize_cut_plane
from floris.optimization.yaw_optimization.yaw_optimizer_sr import YawOptimizationSR
from slsqp_optimization import build_managers, load_config, load_top_saved_pi_layouts


CONFIG_PATH = "configs/denmark.json"
TOP_LAYOUT_COUNT = 1
WAKE_STEERING_DIRNAME = "wake_steering"

MINIMUM_YAW_ANGLE_DEG = -20.0 # Not sure if this doesnt have to be set to 0?
MAXIMUM_YAW_ANGLE_DEG = 20.0
NY_PASSES = [9, 6, 4]
EXCLUDE_DOWNSTREAM_TURBINES = True
OPTIMIZATION_RESTARTS = 3
TOP_FREQUENCY_BINS_TO_OPTIMIZE = 144

COARSE_OPTIMIZATION_D_WD_DEG = 5.0
COARSE_OPTIMIZATION_D_WS_MPS = 2.0

WIND_SPEED_LOW_NO_STEER = 4.0
WIND_SPEED_HIGH_NO_STEER = 14.0
WIND_SPEED_LOW_FULL_STEER = 6.0
WIND_SPEED_HIGH_FULL_STEER = 12.0

GLOBAL_SCALE_GRID = np.linspace(0.0, 1.0, 21)
MIN_EFFECTIVE_YAW_DEG = 0.5


def _ensure_wake_steering_dir(result_writer):
    wake_steering_dir = os.path.join(result_writer.results_dir, WAKE_STEERING_DIRNAME)
    os.makedirs(wake_steering_dir, exist_ok=True)
    return wake_steering_dir


def _get_most_common_bin(wind_rose):
    freq_table = np.asarray(wind_rose.freq_table, dtype=float)
    idx = np.unravel_index(int(np.argmax(freq_table)), freq_table.shape)
    wd = float(np.asarray(wind_rose.wind_directions, dtype=float)[idx[0]])
    ws = float(np.asarray(wind_rose.wind_speeds, dtype=float)[idx[1]])
    return idx, wd, ws, freq_table


def _extract_direction_yaw_mapping(df_opt):
    direction_to_yaw = {}
    for _, row in df_opt.iterrows():
        wd = float(row["wind_direction"])
        direction_to_yaw[wd] = np.asarray(row["yaw_angles_opt"], dtype=float)
    return direction_to_yaw


def _nearest_direction_key(direction_keys, target_wd_deg):
    keys = np.asarray(direction_keys, dtype=float)
    deltas = np.abs(((keys - target_wd_deg + 180.0) % 360.0) - 180.0)
    return float(keys[int(np.argmin(deltas))])


def _apply_speed_ramp(yaw_full, wind_speed):
    if (wind_speed < WIND_SPEED_LOW_NO_STEER) or (wind_speed > WIND_SPEED_HIGH_NO_STEER):
        return np.zeros_like(yaw_full)
    if wind_speed < WIND_SPEED_LOW_FULL_STEER:
        scale = (wind_speed - WIND_SPEED_LOW_NO_STEER) / (
            WIND_SPEED_LOW_FULL_STEER - WIND_SPEED_LOW_NO_STEER
        )
        return yaw_full * np.clip(scale, 0.0, 1.0)
    if wind_speed > WIND_SPEED_HIGH_FULL_STEER:
        scale = (WIND_SPEED_HIGH_NO_STEER - wind_speed) / (
            WIND_SPEED_HIGH_NO_STEER - WIND_SPEED_HIGH_FULL_STEER
        )
        return yaw_full * np.clip(scale, 0.0, 1.0)
    return yaw_full


def _yaw_for_condition(direction_to_yaw, wind_direction, wind_speed, n_turbines):
    nearest_wd = _nearest_direction_key(list(direction_to_yaw.keys()), float(wind_direction))
    yaw_full = np.asarray(direction_to_yaw[nearest_wd], dtype=float)
    if yaw_full.shape[0] != n_turbines:
        raise ValueError(
            f"Yaw vector length {yaw_full.shape[0]} does not match n_turbines={n_turbines}."
        )
    return _apply_speed_ramp(yaw_full, float(wind_speed))


def _build_full_rose_yaw_angles(direction_to_yaw, wind_directions, wind_speeds, n_turbines):
    yaw_angles = np.zeros((len(wind_speeds), n_turbines), dtype=float)
    for i in range(len(wind_speeds)):
        yaw_angles[i, :] = _yaw_for_condition(
            direction_to_yaw=direction_to_yaw,
            wind_direction=wind_directions[i],
            wind_speed=wind_speeds[i],
            n_turbines=n_turbines,
        )
    return yaw_angles


def _get_active_wind_speed_indices(wind_rose, freq_table):
    speeds = np.asarray(wind_rose.wind_speeds, dtype=float)
    frequency_by_speed = np.sum(freq_table, axis=0)
    active_indices = [
        idx
        for idx, ws in enumerate(speeds)
        if frequency_by_speed[idx] > 0.0 and WIND_SPEED_LOW_NO_STEER <= ws <= WIND_SPEED_HIGH_NO_STEER
    ]
    return active_indices


def _build_coarse_wind_rose_from_fine(wind_rose, d_wd_deg, d_ws_mps):
    fine_wd = np.asarray(wind_rose.wind_directions, dtype=float)
    fine_ws = np.asarray(wind_rose.wind_speeds, dtype=float)
    fine_freq = np.asarray(wind_rose.freq_table, dtype=float)

    wd_edges = np.arange(0.0, 360.0 + float(d_wd_deg), float(d_wd_deg))
    ws_max = float(np.max(fine_ws)) if fine_ws.size > 0 else 0.0
    ws_edges = np.arange(0.0, ws_max + float(d_ws_mps) + 1e-9, float(d_ws_mps))

    coarse_wd = 0.5 * (wd_edges[:-1] + wd_edges[1:])
    coarse_ws = 0.5 * (ws_edges[:-1] + ws_edges[1:])
    coarse_freq = np.zeros((coarse_wd.shape[0], coarse_ws.shape[0]), dtype=float)

    wd_idx_map = np.clip((np.floor(np.mod(fine_wd, 360.0) / float(d_wd_deg))).astype(int), 0, coarse_wd.shape[0] - 1)
    ws_idx_map = np.clip((np.floor(np.asarray(fine_ws, dtype=float) / float(d_ws_mps))).astype(int), 0, coarse_ws.shape[0] - 1)

    for i_wd, coarse_i in enumerate(wd_idx_map):
        for i_ws, coarse_j in enumerate(ws_idx_map):
            coarse_freq[coarse_i, coarse_j] += float(fine_freq[i_wd, i_ws])

    return coarse_wd, coarse_ws, coarse_freq


def _select_top_frequency_bins(coarse_wd, coarse_ws, coarse_freq, top_count):
    rows = []
    for i_wd in range(coarse_freq.shape[0]):
        for i_ws in range(coarse_freq.shape[1]):
            freq = float(coarse_freq[i_wd, i_ws])
            if freq <= 0.0:
                continue
            ws_val = float(coarse_ws[i_ws])
            if ws_val < WIND_SPEED_LOW_NO_STEER or ws_val > WIND_SPEED_HIGH_NO_STEER:
                continue
            rows.append(
                {
                    "i_wd": i_wd,
                    "i_ws": i_ws,
                    "wd": float(coarse_wd[i_wd]),
                    "ws": ws_val,
                    "freq": freq,
                }
            )

    rows.sort(key=lambda row: row["freq"], reverse=True)
    return rows[: int(top_count)]


def _group_top_bins_by_speed(top_bins):
    grouped = {}
    for row in top_bins:
        ws = float(row["ws"])
        if ws not in grouped:
            grouped[ws] = []
        grouped[ws].append(row)
    return grouped


def _optimize_yaw_for_one_speed(
    layout_real,
    floris_settings,
    wind_directions,
    wind_speed,
    turbulence_intensity,
    frequency_by_direction,
    n_turbines,
):
    best_score = -np.inf
    best_direction_to_yaw = None

    for restart_idx in range(OPTIMIZATION_RESTARTS):
        exclude_downstream = EXCLUDE_DOWNSTREAM_TURBINES if (restart_idx % 2 == 0) else False

        fmodel_local = FlorisModel(floris_settings["wake_model_path"])
        fmodel_local.set(
            layout_x=layout_real[:, 0],
            layout_y=layout_real[:, 1],
            turbine_type=[floris_settings["turbine_type"]] * n_turbines,
            reference_wind_height=floris_settings["reference_wind_height"],
            wind_shear=floris_settings["wind_shear"],
        )

        ts_for_speed = TimeSeries(
            wind_directions=np.asarray(wind_directions, dtype=float),
            wind_speeds=float(wind_speed),
            turbulence_intensities=float(turbulence_intensity),
        )
        fmodel_local.set(wind_data=ts_for_speed)

        yaw_opt = YawOptimizationSR(
            fmodel=fmodel_local,
            minimum_yaw_angle=MINIMUM_YAW_ANGLE_DEG,
            maximum_yaw_angle=MAXIMUM_YAW_ANGLE_DEG,
            Ny_passes=NY_PASSES,
            exclude_downstream_turbines=exclude_downstream,
        )
        df_speed = yaw_opt.optimize()

        direction_to_yaw = _extract_direction_yaw_mapping(df_speed)
        yaw_matrix = np.vstack(
            [direction_to_yaw[float(wd)] for wd in np.asarray(wind_directions, dtype=float)]
        )
        fmodel_local.set(yaw_angles=yaw_matrix)
        fmodel_local.run()

        power_by_direction = np.asarray(fmodel_local.get_farm_power(), dtype=float).reshape(-1)
        score = float(np.dot(power_by_direction, np.asarray(frequency_by_direction, dtype=float)))

        if score > best_score:
            best_score = score
            best_direction_to_yaw = direction_to_yaw

    if best_direction_to_yaw is None:
        raise RuntimeError(f"No valid yaw solution produced at wind speed {wind_speed:.2f} m/s")

    return best_direction_to_yaw


def _build_multispeed_yaw_map(
    layout_real,
    floris_settings,
    grouped_top_bins_by_speed,
    turbulence_intensity,
    n_turbines,
):
    yaw_map_by_speed = {}
    for ws in sorted(grouped_top_bins_by_speed.keys()):
        rows = grouped_top_bins_by_speed[ws]
        wind_directions = np.asarray([row["wd"] for row in rows], dtype=float)
        freq_by_direction = np.asarray([row["freq"] for row in rows], dtype=float)
        if wind_directions.size == 0 or np.sum(freq_by_direction) <= 0.0:
            continue

        print(
            f"[Yaw] Multi-speed optimization at WS={ws:.2f} m/s "
            f"for {wind_directions.size} top-frequency directions "
            f"with {OPTIMIZATION_RESTARTS} restarts and Ny_passes={NY_PASSES}."
        )

        yaw_map_by_speed[ws] = _optimize_yaw_for_one_speed(
            layout_real=layout_real,
            floris_settings=floris_settings,
            wind_directions=wind_directions,
            wind_speed=ws,
            turbulence_intensity=turbulence_intensity,
            frequency_by_direction=freq_by_direction,
            n_turbines=n_turbines,
        )

    if not yaw_map_by_speed:
        raise RuntimeError("No active wind-speed bins were available for multi-speed yaw optimization.")

    return yaw_map_by_speed


def _select_nearest_speed_key(speed_keys, wind_speed):
    keys = np.asarray(list(speed_keys), dtype=float)
    return float(keys[int(np.argmin(np.abs(keys - float(wind_speed))))])


def _build_full_rose_yaw_angles_multispeed(
    yaw_map_by_speed,
    wind_directions,
    wind_speeds,
    n_turbines,
):
    yaw_angles = np.zeros((len(wind_speeds), n_turbines), dtype=float)
    for i in range(len(wind_speeds)):
        ws = float(wind_speeds[i])
        if ws < WIND_SPEED_LOW_NO_STEER or ws > WIND_SPEED_HIGH_NO_STEER:
            yaw_angles[i, :] = 0.0
            continue

        ws_key = _select_nearest_speed_key(yaw_map_by_speed.keys(), ws)
        direction_to_yaw = yaw_map_by_speed[ws_key]
        yaw_angles[i, :] = _yaw_for_condition(
            direction_to_yaw=direction_to_yaw,
            wind_direction=float(wind_directions[i]),
            wind_speed=ws,
            n_turbines=n_turbines,
        )
    return yaw_angles


def _sparsify_yaw(yaw_angles, min_effective_deg=MIN_EFFECTIVE_YAW_DEG):
    yaw_out = np.asarray(yaw_angles, dtype=float).copy()
    yaw_out[np.abs(yaw_out) < float(min_effective_deg)] = 0.0
    return yaw_out


def _run_aep_with_yaw(fmodel, wind_rose, yaw_angles):
    fmodel.set(wind_data=wind_rose)
    fmodel.set(yaw_angles=np.asarray(yaw_angles, dtype=float))
    fmodel.run()
    return float(fmodel.get_farm_AEP())


def _find_best_global_yaw_scale(fmodel, wind_rose, yaw_angles_candidate, baseline_aep):
    best_alpha = 0.0
    best_aep = float(baseline_aep)
    best_schedule = np.zeros_like(yaw_angles_candidate)

    for alpha in GLOBAL_SCALE_GRID:
        schedule = np.asarray(yaw_angles_candidate, dtype=float) * float(alpha)
        aep_alpha = _run_aep_with_yaw(fmodel, wind_rose, schedule)
        if aep_alpha > best_aep:
            best_aep = float(aep_alpha)
            best_alpha = float(alpha)
            best_schedule = schedule

    return best_alpha, best_aep, best_schedule


def _compute_yaw_stats(yaw_angles, yaw_limit_deg=MAXIMUM_YAW_ANGLE_DEG):
    yaw = np.asarray(yaw_angles, dtype=float)
    total = int(yaw.size)
    non_zero = int(np.sum(np.abs(yaw) > 1e-9))
    at_limit = int(np.sum(np.abs(np.abs(yaw) - float(yaw_limit_deg)) <= 0.05))
    return {
        "mean_abs_yaw_deg": float(np.mean(np.abs(yaw))),
        "max_abs_yaw_deg": float(np.max(np.abs(yaw))) if total > 0 else 0.0,
        "non_zero_fraction": float(non_zero / total) if total > 0 else 0.0,
        "at_limit_fraction": float(at_limit / total) if total > 0 else 0.0,
    }


def _reshape_power_if_needed(power_matrix, freq_table):
    power = np.asarray(power_matrix, dtype=float)
    if power.shape == freq_table.shape:
        return power
    if power.size == freq_table.size:
        return power.reshape(freq_table.shape)
    raise ValueError(
        f"Power array shape {power.shape} cannot be aligned with frequency table {freq_table.shape}."
    )


def _format_gain_line(label, baseline, optimized, unit="-", percent=True, precision=4):
    delta = optimized - baseline
    if baseline == 0:
        rel = np.nan
    else:
        rel = (optimized / baseline - 1.0) * 100.0

    unit_tag = f" [{unit}]" if unit else ""

    if percent:
        return (
            f"{label}{unit_tag}: {baseline:.{precision}f} -> {optimized:.{precision}f} "
            f"(delta {delta:+.{precision}f} {unit}, rel {rel:+.3f}%)"
        )
    return (
        f"{label}{unit_tag}: {baseline:.{precision}f} -> {optimized:.{precision}f} "
        f"(delta {delta:+.{precision}f} {unit})"
    )


def _build_gain_text(metrics):
    lines = [
        "Wake-steering gains (full wind rose):",
        _format_gain_line("PI", metrics["pi_baseline"], metrics["pi_opt"], unit="-", percent=True, precision=6),
        _format_gain_line("IRR", metrics["irr_baseline_pct"], metrics["irr_opt_pct"], unit="%", percent=True, precision=4),
        _format_gain_line("AEP", metrics["aep_baseline_gwh"], metrics["aep_opt_gwh"], unit="GWh", percent=True, precision=6),
        _format_gain_line(
            "Efficiency",
            metrics["efficiency_baseline_pct"],
            metrics["efficiency_opt_pct"],
            unit="%",
            percent=True,
            precision=4,
        ),
        _format_gain_line("LCoE", metrics["lcoe_baseline"], metrics["lcoe_opt"], unit="$/MWh", percent=True, precision=6),
        _format_gain_line(
            "Capacity factor",
            metrics["capacity_factor_baseline"],
            metrics["capacity_factor_opt"],
            unit="-",
            percent=True,
            precision=6,
        ),
        _format_gain_line(
            "Wake loss",
            metrics["wake_loss_baseline_pct"],
            metrics["wake_loss_opt_pct"],
            unit="%",
            percent=True,
            precision=4,
        ),
        f"Installed capacity [MW]: {metrics['installed_mw']:.3f}",
        f"Yaw optimization runtime [s]: {metrics['yaw_runtime_s']:.2f}",
        f"Global yaw scale applied: {metrics['global_yaw_scale']:.2f}",
        (
            "Non-zero yaw fraction (before -> after): "
            f"{metrics['yaw_non_zero_fraction_before']:.3f} -> {metrics['yaw_non_zero_fraction_after']:.3f}"
        ),
        (
            "At-limit yaw fraction (before -> after): "
            f"{metrics['yaw_at_limit_fraction_before']:.3f} -> {metrics['yaw_at_limit_fraction_after']:.3f}"
        ),
        (
            "Mean |yaw| [deg] (before -> after): "
            f"{metrics['mean_abs_yaw_before_deg']:.3f} -> {metrics['mean_abs_yaw_after_deg']:.3f}"
        ),
        f"Yaw optimization wind speed: {metrics['optimization_wind_speed']:.2f} m/s",
    ]
    return "\n".join(lines)


def _overlay_site_boundary(ax, site_polygon):
    if site_polygon is None:
        return
    if site_polygon.geom_type == "MultiPolygon":
        for geom in site_polygon.geoms:
            bx, by = geom.exterior.xy
            ax.plot(bx, by, color="white", linewidth=1.4, alpha=0.9)
        ax.plot([], [], color="white", linewidth=1.4, label="Site boundary")
    elif site_polygon.geom_type == "Polygon":
        bx, by = site_polygon.exterior.xy
        ax.plot(bx, by, color="white", linewidth=1.4, alpha=0.9, label="Site boundary")


def _draw_wind_direction_arrow(ax, wind_direction):
    # Meteorological convention: wind direction is where wind comes from.
    # Arrow shows flow direction (towards where wind goes), i.e. +180 deg.
    theta = np.deg2rad(float(wind_direction) + 180.0)
    length = 0.14
    x0, y0 = 0.08, 0.90
    dx = length * np.sin(theta)
    dy = length * np.cos(theta)
    ax.annotate(
        "",
        xy=(x0 + dx, y0 + dy),
        xytext=(x0, y0),
        xycoords="axes fraction",
        arrowprops={"arrowstyle": "->", "lw": 2.0, "color": "black"},
    )
    ax.text(
        x0,
        y0 + 0.04,
        f"Wind from {float(wind_direction):.1f} deg",
        transform=ax.transAxes,
        fontsize=8,
        ha="left",
        va="bottom",
        bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": "gray", "alpha": 0.9},
    )


def _plot_power_gain_heatmap(output_path, wind_rose, power_baseline, power_opt):
    wind_directions = np.asarray(wind_rose.wind_directions, dtype=float)
    wind_speeds = np.asarray(wind_rose.wind_speeds, dtype=float)
    baseline = np.asarray(power_baseline, dtype=float)
    optimized = np.asarray(power_opt, dtype=float)

    absolute_gain = optimized - baseline
    ratio = np.divide(
        optimized,
        baseline,
        out=np.ones_like(optimized, dtype=float),
        where=np.abs(baseline) > 1e-9,
    )
    relative_gain_pct = (ratio - 1.0) * 100.0

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7), constrained_layout=True)

    im1 = ax1.imshow(absolute_gain, aspect="auto", cmap="RdYlGn")
    cbar1 = fig.colorbar(im1, ax=ax1)
    cbar1.set_label("Power gain [W]")
    ax1.set_title("Absolute power gain by wind bin")
    ax1.set_xlabel("Wind speed [m/s]")
    ax1.set_ylabel("Wind direction [deg]")

    im2 = ax2.imshow(relative_gain_pct, aspect="auto", cmap="RdYlGn")
    cbar2 = fig.colorbar(im2, ax=ax2)
    cbar2.set_label("Relative gain [%]")
    ax2.set_title("Relative power gain by wind bin")
    ax2.set_xlabel("Wind speed [m/s]")
    ax2.set_ylabel("Wind direction [deg]")

    ws_ticks = np.arange(len(wind_speeds))
    wd_ticks = np.arange(len(wind_directions))
    ws_tick_step = max(1, len(ws_ticks) // 10)
    wd_tick_step = max(1, len(wd_ticks) // 12)

    for ax in (ax1, ax2):
        ax.set_xticks(ws_ticks[::ws_tick_step])
        ax.set_xticklabels([f"{ws:.1f}" for ws in wind_speeds[::ws_tick_step]], rotation=45, ha="right")
        ax.set_yticks(wd_ticks[::wd_tick_step])
        ax.set_yticklabels([f"{wd:.1f}" for wd in wind_directions[::wd_tick_step]])

    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def _plot_wake_map_with_yaw_table(
    output_path,
    floris_settings,
    layout_real,
    site_polygon,
    turbulence_intensity,
    wind_direction,
    wind_speed,
    yaw_angles_deg,
    case_title,
    case_note,
    gains_text,
):
    n_turbines = layout_real.shape[0]
    viz_fmodel = FlorisModel(floris_settings["wake_model_path"])
    viz_fmodel.set(
        layout_x=layout_real[:, 0],
        layout_y=layout_real[:, 1],
        wind_speeds=[float(wind_speed)],
        wind_directions=[float(wind_direction)],
        turbulence_intensities=[float(turbulence_intensity)],
        yaw_angles=np.asarray([yaw_angles_deg], dtype=float),
        turbine_type=[floris_settings["turbine_type"]] * n_turbines,
        reference_wind_height=floris_settings["reference_wind_height"],
        wind_shear=floris_settings["wind_shear"],
    )
    viz_fmodel.run()

    horizontal_plane = viz_fmodel.calculate_horizontal_plane(
        height=floris_settings["reference_wind_height"],
        x_resolution=250,
        y_resolution=250,
        findex_for_viz=0,
    )

    fig = plt.figure(figsize=(16, 9))
    grid = fig.add_gridspec(
        2,
        2,
        height_ratios=[4.7, 1.9],
        width_ratios=[4.2, 1.8],
        hspace=0.10,
        wspace=0.14,
    )

    ax_map = fig.add_subplot(grid[0, 0])
    ax_table = fig.add_subplot(grid[0, 1])
    ax_note = fig.add_subplot(grid[1, :])

    visualize_cut_plane(
        horizontal_plane,
        ax=ax_map,
        title=f"{case_title} | WD={wind_direction:.1f} deg, WS={wind_speed:.1f} m/s",
        color_bar=False,
    )

    ax_map.scatter(
        layout_real[:, 0],
        layout_real[:, 1],
        marker="o",
        s=48,
        facecolors="none",
        edgecolors="black",
        linewidths=1.0,
        label="Turbines",
    )
    _overlay_site_boundary(ax_map, site_polygon)
    _draw_wind_direction_arrow(ax_map, wind_direction)

    for turbine_idx, (x_coord, y_coord) in enumerate(layout_real, start=1):
        ax_map.text(
            x_coord,
            y_coord,
            str(turbine_idx),
            fontsize=7,
            ha="center",
            va="center",
            color="black",
            bbox={"boxstyle": "round,pad=0.18", "fc": "white", "ec": "black", "lw": 0.4, "alpha": 0.85},
            zorder=6,
        )

    ax_map.set_aspect("equal")
    ax_map.grid(True, alpha=0.25)
    ax_map.legend(loc="upper right")

    ax_table.axis("off")
    table_rows = [[idx + 1, f"{yaw_angles_deg[idx]:.2f}"] for idx in range(n_turbines)]
    yaw_table = ax_table.table(
        cellText=table_rows,
        colLabels=["Turbine #", "Yaw [deg]"],
        loc="center",
        cellLoc="center",
        colLoc="center",
    )
    yaw_table.auto_set_font_size(False)
    yaw_table.set_fontsize(8)
    yaw_table.scale(1.0, 1.15)
    ax_table.set_title("Yaw offsets relative to wind direction", fontsize=10)

    ax_note.axis("off")
    note_text = f"{case_note}\n\n{gains_text}"
    ax_note.text(
        0.01,
        0.98,
        note_text,
        ha="left",
        va="top",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.5", "fc": "white", "ec": "gray", "alpha": 0.95},
    )

    fig.subplots_adjust(left=0.04, right=0.98, top=0.94, bottom=0.06, wspace=0.14, hspace=0.10)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def _save_yaw_results_csv(output_dir, yaw_map_by_speed):
    csv_path = os.path.join(output_dir, "yaw_angles_by_direction.csv")
    with open(csv_path, mode="w", encoding="utf-8", newline="") as file_obj:
        writer = csv.writer(file_obj)
        writer.writerow(["wind_speed_m_per_s", "wind_direction_deg", "yaw_angles_deg_by_turbine"])
        for ws in sorted(yaw_map_by_speed.keys()):
            direction_to_yaw = yaw_map_by_speed[ws]
            for wd in sorted(direction_to_yaw.keys()):
                yaw_vec = np.asarray(direction_to_yaw[wd], dtype=float)
                writer.writerow([f"{ws:.6f}", f"{wd:.6f}", json.dumps(yaw_vec.tolist())])
    return csv_path


def run_yaw_optimization(config_path=CONFIG_PATH):
    config = load_config(config_path)
    result_writer, optimizer, _, _ = build_managers(config)
    saved_layouts = load_top_saved_pi_layouts(result_writer, top_count=TOP_LAYOUT_COUNT)
    selected_layout = saved_layouts[0]

    layout_id = selected_layout["layout_id"]
    layout_real = np.asarray(selected_layout["coordinates_m"], dtype=float)
    n_turbines = int(selected_layout["num_turbines"])

    wake_steering_dir = _ensure_wake_steering_dir(result_writer)

    wind_rose = optimizer.floris.wind_rose_pi
    dominant_idx, dominant_wd, dominant_ws, freq_table = _get_most_common_bin(wind_rose)

    coarse_wd, coarse_ws, coarse_freq = _build_coarse_wind_rose_from_fine(
        wind_rose=wind_rose,
        d_wd_deg=COARSE_OPTIMIZATION_D_WD_DEG,
        d_ws_mps=COARSE_OPTIMIZATION_D_WS_MPS,
    )
    top_bins = _select_top_frequency_bins(
        coarse_wd=coarse_wd,
        coarse_ws=coarse_ws,
        coarse_freq=coarse_freq,
        top_count=TOP_FREQUENCY_BINS_TO_OPTIMIZE,
    )
    grouped_top_bins_by_speed = _group_top_bins_by_speed(top_bins)
    top_bin_freq_sum = float(sum(row["freq"] for row in top_bins))
    total_freq_sum = float(np.sum(coarse_freq))
    top_bin_frequency_coverage = (top_bin_freq_sum / total_freq_sum) if total_freq_sum > 0.0 else 0.0

    if not top_bins:
        raise RuntimeError("No non-zero coarse-frequency bins were found for yaw optimization.")

    floris_settings = {
        "wake_model_path": optimizer.floris.wake_model_path,
        "turbine_type": optimizer.floris.turbine_type,
        "reference_wind_height": optimizer.floris.reference_wind_height,
        "wind_shear": optimizer.floris.wind_shear,
    }
    turbulence_intensity = float(config.get("wind", {}).get("ti", 0.06))

    fmodel = FlorisModel(floris_settings["wake_model_path"])
    fmodel.set(
        layout_x=layout_real[:, 0],
        layout_y=layout_real[:, 1],
        turbine_type=[floris_settings["turbine_type"]] * n_turbines,
        reference_wind_height=floris_settings["reference_wind_height"],
        wind_shear=floris_settings["wind_shear"],
    )

    # Baseline full-rose run
    fmodel.set(wind_data=wind_rose)
    fmodel.run()
    power_baseline = _reshape_power_if_needed(fmodel.get_farm_power(), freq_table)
    aep_baseline = float(fmodel.get_farm_AEP())
    fmodel.run_no_wake()
    aep_no_wake = float(fmodel.get_farm_AEP())

    print(
        f"[Yaw] Multi-speed optimization for layout {layout_id} with Ny_passes={NY_PASSES} "
        f"and {OPTIMIZATION_RESTARTS} restarts per active speed bin."
    )
    print(
        f"[Yaw] Coarse optimization windrose: d_wd={COARSE_OPTIMIZATION_D_WD_DEG:.1f} deg, "
        f"d_ws={COARSE_OPTIMIZATION_D_WS_MPS:.1f} m/s."
    )
    print(
        f"[Yaw] Optimizing only top {len(top_bins)} coarse frequency bins "
        f"(coverage={top_bin_frequency_coverage * 100.0:.2f}% of coarse windrose frequency mass)."
    )

    start_time = time.time()
    yaw_map_by_speed = _build_multispeed_yaw_map(
        layout_real=layout_real,
        floris_settings=floris_settings,
        grouped_top_bins_by_speed=grouped_top_bins_by_speed,
        turbulence_intensity=turbulence_intensity,
        n_turbines=n_turbines,
    )
    opt_runtime_s = time.time() - start_time
    print(f"[Yaw] Multi-speed optimization finished in {opt_runtime_s:.2f}s")

    # Build candidate full-rose yaw schedule, then sparsify and globally scale to
    # maximize full-rose AEP and avoid unnecessary/high yaw angles.
    wind_directions_full = np.asarray(fmodel.wind_directions, dtype=float)
    wind_speeds_full = np.asarray(fmodel.wind_speeds, dtype=float)
    yaw_angles_raw = _build_full_rose_yaw_angles_multispeed(
        yaw_map_by_speed=yaw_map_by_speed,
        wind_directions=wind_directions_full,
        wind_speeds=wind_speeds_full,
        n_turbines=n_turbines,
    )
    yaw_angles_sparse = _sparsify_yaw(yaw_angles_raw, min_effective_deg=MIN_EFFECTIVE_YAW_DEG)
    best_alpha, aep_opt, yaw_angles_full = _find_best_global_yaw_scale(
        fmodel=fmodel,
        wind_rose=wind_rose,
        yaw_angles_candidate=yaw_angles_sparse,
        baseline_aep=aep_baseline,
    )

    if aep_opt <= aep_baseline:
        raise RuntimeError(
            "No wake-steering schedule improved full-rose AEP. "
            "Per requirement, the script stops instead of accepting power-reducing yaw settings."
        )

    fmodel.set(wind_data=wind_rose)
    fmodel.set(yaw_angles=yaw_angles_full)
    fmodel.run()
    power_opt = _reshape_power_if_needed(fmodel.get_farm_power(), freq_table)
    aep_opt = float(fmodel.get_farm_AEP())

    energy_rose_baseline_wh = np.nan_to_num(power_baseline, nan=0.0) * freq_table * 8760.0
    energy_rose_opt_wh = np.nan_to_num(power_opt, nan=0.0) * freq_table * 8760.0

    pi_baseline, lcoe_baseline = optimizer.econ.calculate_metrics(
        layout_real, aep_baseline, n_turbines, energy_rose_baseline_wh
    )
    pi_opt, lcoe_opt = optimizer.econ.calculate_metrics(
        layout_real, aep_opt, n_turbines, energy_rose_opt_wh
    )

    irr_baseline = float(
        optimizer.econ.calculate_irr(
            layout_real,
            aep_baseline,
            n_turbines,
            energy_rose_wh=energy_rose_baseline_wh,
        )
    )
    irr_opt = float(
        optimizer.econ.calculate_irr(
            layout_real,
            aep_opt,
            n_turbines,
            energy_rose_wh=energy_rose_opt_wh,
        )
    )

    rated_w = float(optimizer.econ.rated_power_kw) * 1000.0 * float(n_turbines)
    capacity_factor_baseline = float(aep_baseline / (rated_w * 24.0 * 365.0))
    capacity_factor_opt = float(aep_opt / (rated_w * 24.0 * 365.0))
    efficiency_baseline_pct = float(100.0 * aep_baseline / aep_no_wake)
    efficiency_opt_pct = float(100.0 * aep_opt / aep_no_wake)
    wake_loss_baseline_pct = float(100.0 - efficiency_baseline_pct)
    wake_loss_opt_pct = float(100.0 - efficiency_opt_pct)

    yaw_stats_raw = _compute_yaw_stats(yaw_angles_raw)
    yaw_stats_final = _compute_yaw_stats(yaw_angles_full)

    weighted_gain_wh = (np.nan_to_num(power_opt, nan=0.0) - np.nan_to_num(power_baseline, nan=0.0)) * freq_table * 8760.0
    optimized_case_idx = np.unravel_index(int(np.argmax(weighted_gain_wh)), weighted_gain_wh.shape)

    wind_directions_bins = np.asarray(wind_rose.wind_directions, dtype=float)
    wind_speeds_bins = np.asarray(wind_rose.wind_speeds, dtype=float)

    common_case = {
        "idx": dominant_idx,
        "wd": float(wind_directions_bins[dominant_idx[0]]),
        "ws": float(wind_speeds_bins[dominant_idx[1]]),
    }
    best_case = {
        "idx": optimized_case_idx,
        "wd": float(wind_directions_bins[optimized_case_idx[0]]),
        "ws": float(wind_speeds_bins[optimized_case_idx[1]]),
    }

    gains = {
        "pi_baseline": float(pi_baseline),
        "pi_opt": float(pi_opt),
        "irr_baseline_pct": float(irr_baseline * 100.0),
        "irr_opt_pct": float(irr_opt * 100.0),
        "aep_baseline_gwh": float(aep_baseline / 1e9),
        "aep_opt_gwh": float(aep_opt / 1e9),
        "efficiency_baseline_pct": efficiency_baseline_pct,
        "efficiency_opt_pct": efficiency_opt_pct,
        "lcoe_baseline": float(lcoe_baseline),
        "lcoe_opt": float(lcoe_opt),
        "capacity_factor_baseline": capacity_factor_baseline,
        "capacity_factor_opt": capacity_factor_opt,
        "wake_loss_baseline_pct": wake_loss_baseline_pct,
        "wake_loss_opt_pct": wake_loss_opt_pct,
        "installed_mw": float((optimizer.econ.rated_power_kw / 1000.0) * n_turbines),
        "yaw_runtime_s": float(opt_runtime_s),
        "global_yaw_scale": float(best_alpha),
        "yaw_non_zero_fraction_before": float(yaw_stats_raw["non_zero_fraction"]),
        "yaw_non_zero_fraction_after": float(yaw_stats_final["non_zero_fraction"]),
        "yaw_at_limit_fraction_before": float(yaw_stats_raw["at_limit_fraction"]),
        "yaw_at_limit_fraction_after": float(yaw_stats_final["at_limit_fraction"]),
        "mean_abs_yaw_before_deg": float(yaw_stats_raw["mean_abs_yaw_deg"]),
        "mean_abs_yaw_after_deg": float(yaw_stats_final["mean_abs_yaw_deg"]),
        "optimization_wind_speed": float(dominant_ws),
    }
    gains_text = _build_gain_text(gains)

    ws_common_key = _select_nearest_speed_key(yaw_map_by_speed.keys(), common_case["ws"])
    ws_best_key = _select_nearest_speed_key(yaw_map_by_speed.keys(), best_case["ws"])

    common_case_yaw = _yaw_for_condition(
        direction_to_yaw=yaw_map_by_speed[ws_common_key],
        wind_direction=common_case["wd"],
        wind_speed=common_case["ws"],
        n_turbines=n_turbines,
    )
    common_case_yaw = _sparsify_yaw(common_case_yaw, min_effective_deg=MIN_EFFECTIVE_YAW_DEG) * best_alpha
    best_case_yaw = _yaw_for_condition(
        direction_to_yaw=yaw_map_by_speed[ws_best_key],
        wind_direction=best_case["wd"],
        wind_speed=best_case["ws"],
        n_turbines=n_turbines,
    )
    best_case_yaw = _sparsify_yaw(best_case_yaw, min_effective_deg=MIN_EFFECTIVE_YAW_DEG) * best_alpha

    i_common, j_common = common_case["idx"]
    i_best, j_best = best_case["idx"]

    common_baseline_power_w = float(power_baseline[i_common, j_common])
    common_opt_power_w = float(power_opt[i_common, j_common])
    common_gain_w = common_opt_power_w - common_baseline_power_w
    common_gain_pct = (
        (common_opt_power_w / common_baseline_power_w - 1.0) * 100.0
        if abs(common_baseline_power_w) > 1e-9
        else 0.0
    )

    best_baseline_power_w = float(power_baseline[i_best, j_best])
    best_opt_power_w = float(power_opt[i_best, j_best])
    best_gain_w = best_opt_power_w - best_baseline_power_w
    best_gain_pct = (
        (best_opt_power_w / best_baseline_power_w - 1.0) * 100.0
        if abs(best_baseline_power_w) > 1e-9
        else 0.0
    )

    common_case_note = (
        "Most common wind condition (max frequency bin). "
        f"Frequency={freq_table[i_common, j_common]:.6f} [-], "
        f"P_baseline={common_baseline_power_w:.3f} W, "
        f"P_optimized={common_opt_power_w:.3f} W, "
        f"delta P={common_gain_w:+.3f} W ({common_gain_pct:+.3f}%)"
    )
    best_case_note = (
        "Most optimized condition (max annualized energy gain contribution bin). "
        f"Delta energy={weighted_gain_wh[i_best, j_best] / 1e6:.6f} MWh/year, "
        f"P_baseline={best_baseline_power_w:.3f} W, "
        f"P_optimized={best_opt_power_w:.3f} W, "
        f"delta P={best_gain_w:+.3f} W ({best_gain_pct:+.3f}%)"
    )

    common_case_png = os.path.join(wake_steering_dir, "wake_map_most_common_condition.png")
    best_case_png = os.path.join(wake_steering_dir, "wake_map_most_optimized_condition.png")
    heatmap_png = os.path.join(wake_steering_dir, "power_gain_heatmap_full_rose.png")

    _plot_wake_map_with_yaw_table(
        output_path=common_case_png,
        floris_settings=floris_settings,
        layout_real=layout_real,
        site_polygon=optimizer.site.site_polygon,
        turbulence_intensity=turbulence_intensity,
        wind_direction=common_case["wd"],
        wind_speed=common_case["ws"],
        yaw_angles_deg=common_case_yaw,
        case_title="Wake steering - most common condition",
        case_note=common_case_note,
        gains_text=gains_text,
    )
    _plot_wake_map_with_yaw_table(
        output_path=best_case_png,
        floris_settings=floris_settings,
        layout_real=layout_real,
        site_polygon=optimizer.site.site_polygon,
        turbulence_intensity=turbulence_intensity,
        wind_direction=best_case["wd"],
        wind_speed=best_case["ws"],
        yaw_angles_deg=best_case_yaw,
        case_title="Wake steering - most optimized condition",
        case_note=best_case_note,
        gains_text=gains_text,
    )

    _plot_power_gain_heatmap(
        output_path=heatmap_png,
        wind_rose=wind_rose,
        power_baseline=power_baseline,
        power_opt=power_opt,
    )

    yaw_csv_path = _save_yaw_results_csv(wake_steering_dir, yaw_map_by_speed)

    summary = {
        "config_path": config_path,
        "source_layout_id": layout_id,
        "source_layout_num_turbines": n_turbines,
        "yaw_optimization_runtime_s": float(opt_runtime_s),
        "dominant_wind_for_optimization": {
            "wind_direction_deg": float(dominant_wd),
            "wind_speed_m_per_s": float(dominant_ws),
        },
        "most_common_case": {
            "wind_direction_deg": float(common_case["wd"]),
            "wind_speed_m_per_s": float(common_case["ws"]),
            "frequency": float(freq_table[i_common, j_common]),
            "yaw_angles_deg": common_case_yaw.tolist(),
            "reference_optimized_speed_bin_m_per_s": float(ws_common_key),
        },
        "most_optimized_case": {
            "wind_direction_deg": float(best_case["wd"]),
            "wind_speed_m_per_s": float(best_case["ws"]),
            "annualized_gain_mwh": float(weighted_gain_wh[i_best, j_best] / 1e6),
            "yaw_angles_deg": best_case_yaw.tolist(),
            "reference_optimized_speed_bin_m_per_s": float(ws_best_key),
        },
        "gains": gains,
        "yaw_diagnostics": {
            "raw_schedule": yaw_stats_raw,
            "final_schedule": yaw_stats_final,
            "global_scale_applied": float(best_alpha),
            "active_speed_bins_optimized_m_per_s": [float(ws) for ws in sorted(yaw_map_by_speed.keys())],
            "coarse_optimization_settings": {
                "d_wd_deg": float(COARSE_OPTIMIZATION_D_WD_DEG),
                "d_ws_m_per_s": float(COARSE_OPTIMIZATION_D_WS_MPS),
                "top_frequency_bins_optimized": int(len(top_bins)),
                "top_frequency_coverage_fraction": float(top_bin_frequency_coverage),
            },
            "top_frequency_bins": top_bins,
        },
        "outputs": {
            "wake_map_most_common_condition": common_case_png,
            "wake_map_most_optimized_condition": best_case_png,
            "power_gain_heatmap_full_rose": heatmap_png,
            "yaw_schedule_csv": yaw_csv_path,
        },
    }

    summary_path = os.path.join(wake_steering_dir, "wake_steering_summary.json")
    with open(summary_path, mode="w", encoding="utf-8") as file_obj:
        json.dump(summary, file_obj, indent=2)

    print("[Yaw] Wake steering completed.")
    print(f"[Yaw] Source layout: {layout_id} (N={n_turbines})")
    print(f"[Yaw] Baseline AEP: {aep_baseline / 1e9:.6f} GWh")
    print(f"[Yaw] Optimized AEP: {aep_opt / 1e9:.6f} GWh")
    print(f"[Yaw] Relative AEP uplift: {(aep_opt / aep_baseline - 1.0) * 100.0:+.4f}%")
    print(f"[Yaw] Best global yaw scale: {best_alpha:.2f}")
    print(f"[Yaw] Wake steering folder: {wake_steering_dir}")


if __name__ == "__main__":
    try:
        run_yaw_optimization()
    except Exception as exc:
        print(f"Execution failed: {exc}")
        traceback.print_exc()
