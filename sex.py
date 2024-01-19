import plotly.graph_objects as go
import pandas as pd

from lib.transformations import *
from lib.geo import *
from lib.style import *

HEADING_REGION = "Sex Distribution by NUTS3 Region"

UNSELECTED_OPACITY = .2

MAX_GEOS_AT_ONCE = 10


POP_AGE_GROUPS_FINE = {
    "Y_LT5": { "label": "0-4", "median": 2 },
    "Y5-9": { "label": "5-9", "median": 7 },
    "Y10-14": { "label": "10-14", "median": 12 },
    "Y15-19": { "label": "15-19", "median": 17 },
    "Y20-24": { "label": "20-24", "median": 22 },
    "Y25-29": { "label": "25-29", "median": 27 },
    "Y30-34": { "label": "30-34", "median": 32 },
    "Y35-39": { "label": "35-39", "median": 37 },
    "Y40-44": { "label": "40-44", "median": 42 },
    "Y45-49": { "label": "45-49", "median": 47 },
    "Y50-54": { "label": "50-54", "median": 52 },
    "Y55-59": { "label": "55-59", "median": 57 },
    "Y60-64": { "label": "60-64", "median": 62 },
    "Y65-69": { "label": "65-69", "median": 67 },
    "Y70-74": { "label": "70-74", "median": 72 },
    "Y75-79": { "label": "75-79", "median": 77 },
    "Y80-84": { "label": "80+", "median": 82 },
    "Y85-89": { "label": "80+", "median": 87 },
    "Y_GE90": { "label": "90+", "median": 92 },
}

HOVER_TEMPLATE = "<b>%{customdata}</b>: %{y:.2f}%"

df_sex = pd.read_csv("data/population_january1st_fine.tsv", dtype={'geo': str})
df_sex = sort_to_numeric_ffill(df_sex)
df_sex = assign_urbanization_type(df_sex)
df_sex = df_sex[df_sex['age'].isin(POP_AGE_GROUPS_FINE.keys())]

df_sex['age_median'] = df_sex['age'].apply(lambda x: POP_AGE_GROUPS_FINE[x]['median'] )
df_sex['age_label'] = df_sex['age'].apply(lambda x: POP_AGE_GROUPS_FINE[x]['label'])
years_sex = get_years(df_sex)

def create_sex_violin_plot(fig, geos=[], year='2022', selected=[]):
    global df_sex
    if year is not None and year not in years_sex:
        raise NoDataAvailableError(year=year)
    
    df_sex_use = df_sex
    fig = create_figure()
    if geos is None or len(geos) == 0:
        geos = df_sex_use['geo'].unique()
    else:
        df_sex_use = df_sex_use[df_sex_use['geo'].isin(geos)]

    if len(geos) > MAX_GEOS_AT_ONCE:
        if selected is not None and len(selected) > 0:
            if len(intersection(URBAN_TYPES.values(), selected)) == 0:
                selected = get_urban_types_of_geos(selected)
        df_sex_use = df_sex_use.groupby(['urban_type', 'age', 'age_median', 'age_label', 'sex'])[years_sex].sum().reset_index()

        for urban_type in set(df_sex_use['urban_type'].unique().tolist()) - {'unavailable'}:
            row = df_sex_use[df_sex_use['urban_type'] == urban_type].reset_index()
            opacity = 1 if urban_type in selected else UNSELECTED_OPACITY if selected is not None and len(selected) > 0 else 1
            female_proportion = row[row['sex'] == "F"][year].reset_index(drop=True).div(row[row['sex'] == "T"][year].reset_index(drop=True)) * 100
            male_proportion = (row[row['sex'] == "M"][year].reset_index(drop=True)/row[row['sex'] == "T"][year].reset_index(drop=True)) * 100

            y_female = row[row['sex'] == 'F']['age_median'].reset_index(drop=True).repeat(female_proportion)
            y_male = row[row['sex'] == 'M']['age_median'].reset_index(drop=True).repeat(male_proportion)

            fig.add_trace(
                go.Violin(
                    x=row['urban_type'].unique().repeat(y_female.count()),
                    y=y_female,
                    name=f"female ({urban_type})",
                    legendgroup='female',
                    scalegroup='female',
                    side='negative',
                    customdata=row['age_label'],
                    scalemode='count',
                    line_color=add_opacity_to_color(sample_color(URBAN_TYPE_COLORSCALES[urban_type], 1, 5), opacity=opacity),
                    hovertemplate=HOVER_TEMPLATE,
                    hoveron='violins+kde',
                    meanline={'visible': True}
                )
            )

            fig.add_trace(
                go.Violin(
                    x=row['urban_type'].unique().repeat(y_male.count()),
                    y=y_male,
                    name=f"male ({urban_type})",
                    legendgroup='male',
                    scalegroup='male',
                    side='positive',
                    customdata=row['age_label'],
                    scalemode='count',
                    line_color=add_opacity_to_color(sample_color(URBAN_TYPE_COLORSCALES[urban_type], 3, 5), opacity=opacity),
                    hovertemplate=HOVER_TEMPLATE,
                    hoveron='violins+kde',
                    meanline={'visible': True}
                )
            )
    else:
        for geo in geos:
            row = df_sex_use[df_sex_use['geo'] == geo]
            opacity = 1 if geo in selected else UNSELECTED_OPACITY if selected is not None and len(selected) > 0 else 1

            female_proportion = row[row['sex'] == "F"][year].reset_index(drop=True).div(row[row['sex'] == "T"][year].reset_index(drop=True)) * 100
            male_proportion = (row[row['sex'] == "M"][year].reset_index(drop=True)/row[row['sex'] == "T"][year].reset_index(drop=True)) * 100

            y_female = row[row['sex'] == 'F']['age_median'].reset_index(drop=True).repeat(female_proportion)
            y_male = row[row['sex'] == 'M']['age_median'].reset_index(drop=True).repeat(female_proportion)

            urban_type = get_urban_types_of_geos([geo], as_string=True, unique=False).unique()[0]

            fig.add_trace(
                go.Violin(
                    x=row['geo'].unique().repeat(y_female.count()),
                    y=y_female,
                    name=f"female ({geo})",
                    legendgroup='female',
                    scalegroup='female',
                    side='negative',
                    customdata=row['age_label'],
                    scalemode='count',
                    line_color=add_opacity_to_color(sample_color(URBAN_TYPE_COLORSCALES[urban_type], 2, 5), opacity=opacity),
                    hovertemplate=HOVER_TEMPLATE,
                    hoveron='violins+kde',
                    meanline={'visible': True}
                )
            )

            fig.add_trace(
                go.Violin(
                    x=row['geo'].unique().repeat(y_male.count()),
                    y=y_male,
                    name=f"male ({geo})",
                    legendgroup='male',
                    scalegroup='male',
                    side='positive',
                    customdata=row['age_label'],
                    scalemode='count',
                    line_color=add_opacity_to_color(sample_color(URBAN_TYPE_COLORSCALES[urban_type], 4, 5), opacity=opacity),
                    hovertemplate=HOVER_TEMPLATE,
                    hoveron='violins+kde',
                    meanline={'visible': True}
                )
            )
    return fig
        


    