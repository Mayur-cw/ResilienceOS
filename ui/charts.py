import plotly.express as px

def render_line_chart(df):
    # Create a line chart with your theme's brand colors
    fig = px.line(
        df, 
        y=["Income", "Expenses"], 
        color_discrete_sequence=["#8FD9FF", "#02C39A"]
    )

    # Make the background transparent to match your dark theme
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#A0AEC0"),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    return fig