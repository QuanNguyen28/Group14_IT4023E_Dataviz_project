"""Plotly and CSS theme constants."""

PLOTLY_TEMPLATE = "plotly_white"
NAVY = "#0C2235"
TEXT = "#122033"
MUTED = "#667A94"
RED = "#D94C45"
ORANGE = "#E69A1C"
GREEN = "#0F8B5F"
BLUE = "#2F6DE1"
PURPLE = "#7C5CDB"
TEAL = "#118A8A"
CARD_BORDER = "#D8E2EE"
PLOT_BG = "#FBFCFE"
PLOT_GRID = "#EAF0F6"
COLORWAY = [RED, ORANGE, BLUE, TEAL, PURPLE, GREEN]

FONT_FAMILY = '"Avenir Next", "SF Pro Display", "Helvetica Neue", "Segoe UI", sans-serif'


def apply_common_layout(fig, height: int = 360):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        height=height,
        margin=dict(l=18, r=18, t=72, b=74),
        font=dict(family=FONT_FAMILY, color=TEXT, size=13),
        title=dict(font=dict(size=16, color=TEXT, family=FONT_FAMILY), x=0.02, xanchor="left", y=0.96),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PLOT_BG,
        hovermode="closest",
        hoverlabel=dict(bgcolor="white", bordercolor=CARD_BORDER, font_size=12, font_color=TEXT),
        colorway=COLORWAY,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.16,
            xanchor="left",
            x=0,
            bgcolor="rgba(255,255,255,.72)",
            bordercolor="#D8E2EE",
            borderwidth=1,
            font=dict(size=11),
            title=dict(font=dict(size=11, color=MUTED)),
        ),
        coloraxis_colorbar=dict(
            title_font=dict(size=11),
            tickfont=dict(size=10),
            outlinewidth=0,
            bgcolor="rgba(255,255,255,.86)",
        ),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=PLOT_GRID,
        zeroline=False,
        linecolor="#D7E0ED",
        tickfont=dict(color=MUTED, size=11),
        title_font=dict(color=MUTED, size=12),
    )
    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#D7E0ED",
        tickfont=dict(color=MUTED, size=11),
        title_font=dict(color=MUTED, size=12),
    )
    return fig
