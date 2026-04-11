#!/usr/bin/env python3
import csv
#from datetime import datetime
from datetime import datetime, timedelta
from pathlib import Path

INPUT = Path('Blood_Pressure_Log.csv')
#OUTPUT = Path('blood_pressure_j_line_chart.svg')
OUTPUT = Path('C:/Users/sharo/GitHub/SharonAnne.github.io/blood_pressure_j_line_chart.svg')

YEAR = 2026
GOAL_SYS = 130
GOAL_DIA = 80

rows = []
with INPUT.open(newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        if (r.get('Patient') or '').strip() != 'J':
            continue
        date_s = (r.get('Date') or '').strip()
        time_s = (r.get('Time') or '').strip()
        try:
            dt = datetime.strptime(f"{date_s}-{YEAR} {time_s}", "%d-%b-%Y %I:%M %p")
            sys = float((r.get('Systolic') or '').strip())
            dia = float((r.get('Diastolic') or '').strip())
            pulse = float((r.get('Pulse') or '').strip())
        except Exception:
            continue
        #rows.append((dt, sys, dia))
        rows.append((dt, sys, dia, pulse))

rows.sort(key=lambda x: x[0])
if not rows:
    raise SystemExit('No data for patient J')

# Chart layout
W, H = 1100, 650
m_left, m_right, m_top, m_bottom = 90, 40, 70, 90
pw, ph = W - m_left - m_right, H - m_top - m_bottom

min_t = min(r[0] for r in rows)
max_t = max(r[0] for r in rows)
first_midnight = datetime(min_t.year, min_t.month, min_t.day)
last_midnight  = datetime(max_t.year, max_t.month, max_t.day)
#min_bp = min(min(r[1], r[2]) for r in rows)
#max_bp = max(max(r[1], r[2]) for r in rows)
min_bp = min(min(r[1], r[2], r[3]) for r in rows)
max_bp = max(max(r[1], r[2], r[3]) for r in rows)

# Padding for y-axis
min_bp = int(min_bp - 5)
max_bp = int(max_bp + 5)

# Prevent division by zero
span_t = (max_t - min_t).total_seconds() or 1
span_bp = (max_bp - min_bp) or 1

def x_of(dt):
    return m_left + ((dt - min_t).total_seconds() / span_t) * pw

def y_of(v):
    return m_top + (1 - (v - min_bp) / span_bp) * ph

#sys_points = [(x_of(dt), y_of(sys)) for dt, sys, _ in rows]
#dia_points = [(x_of(dt), y_of(dia)) for dt, _, dia in rows]
sys_points = [(x_of(dt), y_of(sys)) for dt, sys, _, _ in rows]
dia_points = [(x_of(dt), y_of(dia)) for dt, _, dia, _ in rows]
pulse_bars = [(x_of(dt), y_of(pulse), pulse) for dt, _, _, pulse in rows]

# Build SVG
parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
parts.append('<rect width="100%" height="100%" fill="white"/>')
parts.append('<text x="550" y="36" text-anchor="middle" font-size="28" font-family="Arial" font-weight="bold">Blood Pressure Trend for Patient J</text>')
parts.append('<text x="550" y="60" text-anchor="middle" font-size="14" font-family="Arial" fill="#555">Systolic and Diastolic over time</text>')

# Grid + y ticks
for i in range(6):
    v = min_bp + i * (span_bp / 5)
    y = y_of(v)
    parts.append(f'<line x1="{m_left}" y1="{y:.2f}" x2="{W-m_right}" y2="{y:.2f}" stroke="#e5e7eb" stroke-width="1"/>')
    parts.append(f'<text x="{m_left-10}" y="{y+5:.2f}" text-anchor="end" font-size="12" font-family="Arial" fill="#444">{v:.0f}</text>')

# x ticks per point
#for dt, _, _, _ in rows:
#    x = x_of(dt)
#    label = dt.strftime('%d-%b %I:%M %p')
#    parts.append(f'<line x1="{x:.2f}" y1="{m_top}" x2="{x:.2f}" y2="{H-m_bottom}" stroke="#f0f0f0" stroke-width="1"/>')
#    parts.append(f'<text x="{x:.2f}" y="{H-m_bottom+22}" text-anchor="end" transform="rotate(-35 {x:.2f},{H-m_bottom+22})" font-size="11" font-family="Arial" fill="#444">{label}</text>')

# x ticks at midnight of each day
tick_dt = first_midnight
while tick_dt <= last_midnight + timedelta(days=1):
    if min_t <= tick_dt <= max_t:
        x = x_of(tick_dt)
        label = tick_dt.strftime('%d-%b')
        parts.append(f'<line x1="{x:.2f}" y1="{m_top}" x2="{x:.2f}" y2="{H-m_bottom}" stroke="#f0f0f0" stroke-width="1"/>')
        #parts.append(f'<text x="{x:.2f}" y="{H-m_bottom+22}" text-anchor="middle" font-size="11" font-family="Arial" fill="#444">{label}</text>')
        parts.append(f'<text x="{x:.2f}" y="{H-m_bottom+22}" text-anchor="end" transform="rotate(-35 {x:.2f},{H-m_bottom+22})" font-size="11" font-family="Arial" fill="#444">{label}</text>')
    tick_dt += timedelta(days=1)

# axes
parts.append(f'<line x1="{m_left}" y1="{H-m_bottom}" x2="{W-m_right}" y2="{H-m_bottom}" stroke="#111" stroke-width="1.5"/>')
parts.append(f'<line x1="{m_left}" y1="{m_top}" x2="{m_left}" y2="{H-m_bottom}" stroke="#111" stroke-width="1.5"/>')

# pulse bars
bar_w = 10
for x, y, pulse in pulse_bars:
    bar_x = x - bar_w / 2
    bar_y = y
    bar_h = (H - m_bottom) - y
    parts.append(
        f'<rect x="{bar_x:.2f}" y="{bar_y:.2f}" width="{bar_w}" height="{bar_h:.2f}" '
        f'fill="#16a34a" fill-opacity="0.55" stroke="#15803d" stroke-width="1"/>'
    )

# goal lines (draw after bars, before line series)
y_goal_sys = y_of(GOAL_SYS)
y_goal_dia = y_of(GOAL_DIA)

parts.append(
    f'<line x1="{m_left}" y1="{y_goal_sys:.2f}" x2="{W-m_right}" y2="{y_goal_sys:.2f}" '
    f'stroke="#2563eb" stroke-width="2" stroke-dasharray="8,6"/>'
)

parts.append(
    f'<line x1="{m_left}" y1="{y_goal_dia:.2f}" x2="{W-m_right}" y2="{y_goal_dia:.2f}" '
    f'stroke="#dc2626" stroke-width="2" stroke-dasharray="8,6"/>'
)

# lines
sys_path = ' '.join(f'{x:.2f},{y:.2f}' for x, y in sys_points)
dia_path = ' '.join(f'{x:.2f},{y:.2f}' for x, y in dia_points)
parts.append(f'<polyline points="{sys_path}" fill="none" stroke="#2563eb" stroke-width="3"/>')
parts.append(f'<polyline points="{dia_path}" fill="none" stroke="#dc2626" stroke-width="3"/>')

# points
#for x, y in sys_points:
#    parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="#2563eb"/>')
for dt, sys, dia, pulse in rows:
    x = x_of(dt)
    y = y_of(sys)
    parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="#2563eb"/>')
    parts.append(
        f'<text x="{x+8:.2f}" y="{y:.2f}" font-size="11" font-family="Arial" '
        f'fill="#2563eb" dominant-baseline="middle">{sys:.0f}</text>'
    )


#for x, y in dia_points:
#    parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="#dc2626"/>')
for dt, sys, dia, pulse in rows:
    x = x_of(dt)
    y = y_of(dia)
    parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="#dc2626"/>')
    parts.append(
        f'<text x="{x+8:.2f}" y="{y:.2f}" font-size="11" font-family="Arial" '
        f'fill="#dc2626" dominant-baseline="middle">{dia:.0f}</text>'
    )


# labels
parts.append(f'<text x="{m_left + pw/2:.2f}" y="{H-18}" text-anchor="middle" font-size="14" font-family="Arial">Date / Time</text>')
parts.append(f'<text x="24" y="{m_top + ph/2:.2f}" text-anchor="middle" transform="rotate(-90 24,{m_top + ph/2:.2f})" font-size="14" font-family="Arial">Blood Pressure (mmHg)</text>')

# legend
#lx, ly = W - 220, m_top + 10
#lx, ly = m_left + 10, H - m_bottom - 64
lx, ly = m_left + 10, H - m_bottom - 126
#parts.append(f'<rect x="{lx}" y="{ly}" width="180" height="54" fill="white" stroke="#ddd"/>')
#parts.append(f'<rect x="{lx}" y="{ly}" width="180" height="76" fill="white" stroke="#ddd"/>')
parts.append(f'<rect x="{lx}" y="{ly}" width="200" height="116" fill="white" stroke="#ddd"/>')
parts.append(f'<line x1="{lx+12}" y1="{ly+18}" x2="{lx+42}" y2="{ly+18}" stroke="#2563eb" stroke-width="3"/>')
parts.append(f'<text x="{lx+50}" y="{ly+22}" font-size="13" font-family="Arial">Systolic</text>')
parts.append(f'<line x1="{lx+12}" y1="{ly+38}" x2="{lx+42}" y2="{ly+38}" stroke="#dc2626" stroke-width="3"/>')
parts.append(f'<text x="{lx+50}" y="{ly+42}" font-size="13" font-family="Arial">Diastolic</text>')
parts.append(f'<rect x="{lx+12}" y="{ly+48}" width="30" height="10" fill="#16a34a" fill-opacity="0.55" stroke="#15803d" stroke-width="1"/>')
parts.append(f'<text x="{lx+50}" y="{ly+57}" font-size="13" font-family="Arial">Pulse</text>')
parts.append(f'<line x1="{lx+12}" y1="{ly+78}" x2="{lx+42}" y2="{ly+78}" stroke="#2563eb" stroke-width="2" stroke-dasharray="8,6"/>')
parts.append(f'<text x="{lx+50}" y="{ly+82}" font-size="13" font-family="Arial">Goal - Systolic</text>')
parts.append(f'<line x1="{lx+12}" y1="{ly+98}" x2="{lx+42}" y2="{ly+98}" stroke="#dc2626" stroke-width="2" stroke-dasharray="8,6"/>')
parts.append(f'<text x="{lx+50}" y="{ly+102}" font-size="13" font-family="Arial">Goal - Diastolic</text>')


parts.append('</svg>')
OUTPUT.write_text('\n'.join(parts), encoding='utf-8')
print(f'Wrote {OUTPUT}')
