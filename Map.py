# IMPORTS
import folium
import matplotlib.pyplot as plt
import matplotlib
import geopandas as gpd
import pandas as pd
import branca
import branca.colormap as cm
import numpy as np


class Map:

    def __init__(self, latitude, longitude, zoom_start=10, tiles='CartoDB positron'):
        '''
        This method instantiates a new map.

        :param latitude: float
            Latitude of the point at the center of the Map (EPSG: 4326, a.k.a
        Google coordinates)
        :param longitude: float
            Longitude of the point at the center of the Map (EPSG: 4326, a.k.a
        Google coordinates)
        :param zoom_start: int
            The higher the value, the closer you are.
        :param tiles: string
            Defines the type of map background. Possible values include:
                - 'CartoDB positron'
                - 'OpenStreetMap'
                - 'Stamen terrain'
            More background maps available at: https://python-visualization.github.io/folium/modules.html#:~:text=%E2%80%9Ctiles%E2%80%9D%20keyword%3A,leaflet%2Dproviders/preview/
        '''

        # Create the folium map
        self.map = folium.Map(location=[latitude, longitude], zoom_start=zoom_start, tiles=tiles)
        self.value = 5


    def add_layer(self, df_assets, column_geometry, column_value=None, column_id=None, palette='PuOr', legend_label=None, min_value=None, max_value=None, n_colors=100, multi_color=True,
    single_color='red', show_missing=False, show_colorbar=False, color_weight=3, line_thickness=3, marker_radius=1):
        '''
        This method creates a new layer on map.

        :param df_assets: dataframe
            dataframe we want to use create a layer on map.
        :param column_geometry: geometry
            column_geometry is the geometry of the dataframe we are using
            to generate a layer.
        :param column_value: string
            column_value is the column name of the dataframe we want to
            generate a layer.
            Default value: None
        :param column_id: string
            column_id is the name of the id
            Default value: None
        :param palette: string
            Defines the type of palette we want to use to generate colormap.
            Possible values include:
                - 'PuOr'
                - 'RdBu'
                - 'PiYG'
            More colors for colormap available at: https://matplotlib.org/stable/tutorials/colors/colormaps.html
        :param legend_label: string
            legend_label is the name of layer you want to give
        :param min_value: float
            min_value is the minimum value of column_value.
        :param max_value: float
            max_value is the maximum value of column_value.
        :param n_colors: int
            n_colors is the number of colors you want to generate for colormap.
            Default value: 100
            Possible values include:
                - 1,2,....
        :param multi_color: bool
            multi_color is whether we want to display multiple colors
            for point on map.
            Default value: True
        :param single_color: string
            single_color generates single color for all points on map.
            used when multi_color=False
            Default value: 'red'
            Possible values include:
                - 'blue'
                - 'green'
                - 'grey'
            More colors available at: https://www.color-hex.com/
                                      https://www.mathsisfun.com/hexadecimal-decimal-colors.html#:~:text=Some%20Common%20Colors-,Color,(,-255%2C%200%2C255)
        :param show_missing: bool
            Defines whether the column_value has missing values or not.
            Default value: False
        :param show_colorbar: bool
            Defines whether you want to display colorbar for the layer or not.
            Default value: False
        :param color_weight: int
            Defines the weight of color on map.
            Default value: 3
        :param line_thickness: int
            Defines the thickness of line on the map.
            Default value: 3
            Possible values include:
                - 1,2,....
        :param marker_radius: int
            Defines the size of the point on the map.
            Default value: 1
            Possible values include:
                - 1,2,....
        '''

        # Determine legend_name
        if legend_label != None:
            legend_name = legend_label
        elif (legend_label == None) & (column_value == None):
            legend_name = input('Enter the layer name:')
        else:
            legend_name = column_value

        # Creating a copy of df_assets
        df = df_assets.copy()

        # Execute below statements if column_value and legend_name is same
        if column_value != None:
            # Creating a layer
            # 1. Checking whether a column_value is continuous or categorical
            # sorting the dataframe by ascending order of the relevant parameter
            # reindexing is used to make sure that the first value has for index 0
            df_sorted = df.sort_values(by=legend_name).reset_index(drop=True).copy()

            # creating a boolean stating if the feature we study is continuous or categorical.
            continuous = type(df_sorted[legend_name][0]) not in [str, bool]

            # Create count for continuous and categorical
            count_con = 0
            count_cat = 0
            if continuous:
                count_con += 1
            else:
                count_cat += 1

            # 2. Creating a colormap for the map
            # if column_value continuous
            if continuous:
                # if multi_color is True
                if multi_color == True:
                    # Instantiate colormap
                    cmap = plt.cm.get_cmap(palette, n_colors)
                    # Check if min_value of column is None then update it minimum value of column
                    if min_value == None:
                        min_value_update = df[legend_name].min()
                    else:
                        # If min_value is not None keep the user value
                        min_value_update = min_value
                    # Check if max_value of column is None then update it maximum value of column
                    if max_value == None:
                        max_value_update = df[legend_name].max()
                    else:
                        # If max_value is not None keep the user value
                        max_value_update = max_value
                    # Create a colormap for the points
                    colormap = cm.LinearColormap(colors=tuple([tuple(x) for x in cmap(range(n_colors))]),
                                 index=np.linspace(min_value_update, max_value_update, cmap.N),
                                 vmin=min_value_update, vmax=max_value_update, caption= legend_name)

                    # Add the colormap to the map
                    colormap.add_to(self.map)


                    # Converting list of tuples to list of lists
                    cmap_list = [list(tuple(x)) for x in cmap(range(n_colors))]

                    # Empty list
                    color_value = []

                    # Append hexadecimal values to the above list
                    for i in range(len(cmap_list)):
                        colors = matplotlib.colors.rgb2hex(cmap_list[i])
                        color_value.append(colors)


                    # Creating a color column for pipes
                    df['color'] = df[legend_name].apply(lambda x: color_value[int((x-min_value_update)/(max_value_update-min_value_update)*(cmap.N-1))] if ~np.isnan(x) else 'Unknown')





            else:
                # if multi_color is True
                if multi_color == True:
                    n = df[legend_name].nunique()

                    # Instantiate colormap
                    cmap = plt.cm.get_cmap(palette)

                    # List of tuples
                    cmap_list = list(cmap.colors)

                    # Create a list of lists
                    cmap_list_of_lists = [list(ele) for ele in cmap_list]

                    # Append transparency value to each RGB value for hexadecimal conversion
                    for i in range(len(cmap_list_of_lists)):
                        cmap_list_of_lists[i].append(1.0)

                    # Create an empty list or hexadecimal values
                    color_value = []

                    # Append the hexadecimal values to above list
                    for i in range(len(cmap_list_of_lists)):
                        colors = matplotlib.colors.rgb2hex(cmap_list_of_lists[i])
                        color_value.append(colors)

                    # Select first n unique hexadecimal color values from list
                    color_value = color_value[:n]


                    # Mapping unique values of column with colormap
                    # List of unique values of column
                    keys = list(df[df[legend_name].notna()][legend_name].unique())

                    # Instantiate empty dictionary
                    dic_colors = dict()

                    # Counter
                    p = 0

                    # Assign colors to unique values of column
                    for key in keys:
                        dic_colors[key] = color_value[p]
                        p = p+1

                    dic_colors[None] = 'Unknown'
                    dic_colors[np.nan] = 'Unknown'

                    self.dic_colors = dic_colors

                    # Apply the dictionary to each pipe
                    df['color'] = df[legend_name].apply(lambda x:dic_colors[x])
                    self.df = df.copy()




        # 3. Determine the geometry type
        geom = df[column_geometry].type[0]

        # Preparing the geometry of tuples for PolyLine
        if (geom == 'LineString') | (geom == 'Point'):
            df['points'] = df.apply(lambda x: [ (y[1],y[0]) for y in x[column_geometry].coords], axis=1)



        # 4. Plot the layer on the map
        # if multi_color is True
        if multi_color:
            # Splitting null values from non-null
            df_not_null = df[df[legend_name].notna()]
            df_null = df[df[legend_name].isnull()]
            if geom == 'LineString':
                # Create a feature group
                layer = folium.FeatureGroup(name=legend_name, show=False)

                # Not null values
                for _, c in df_not_null.iterrows():
                    # add the line on the map
                    folium.PolyLine(c['points'], weight=color_weight, color=c['color']).add_to(layer)

                if show_missing:
                    # Null values
                    for _, c in df_null.iterrows():
                        # add the line on the map
                        folium.PolyLine(c['points'], weight=color_weight, color='grey').add_to(layer)
                # Add the layer to Map
                layer.add_to(self.map)

            if geom == 'Point':
                # Create a feature group
                layer = folium.FeatureGroup(name=legend_name, show=False)

                # Not null values
                for _, c in df_not_null.iterrows():
                    # add the line on the map
                    folium.CircleMarker(location = [c['points'][0][0], c['points'][0][1]], radius=marker_radius, color=c['color']).add_to(layer)

                if show_missing:
                    # Null values
                    for _, c in df_null.iterrows():
                        # add the line on the map
                        folium.CircleMarker(location = [c['points'][0][0], c['points'][0][1]], radius=marker_radius, color='grey').add_to(layer)
                # Add the layer to Map
                layer.add_to(self.map)

            if geom == 'Polygon':
                # Not null values
                geo_data = gpd.GeoSeries(df_not_null.set_index(column_id)[column_geometry]).to_json()
                folium.Choropleth(geo_data=geo_data,
                                  name=legend_name,
                                  data=df_not_null,
                                  columns=[column_id, legend_name],
                                  key_on='feature.'+column_id,
                                  fill_color=palette,
                                  fill_opacity=0.5,
                                  line_opacity=0.1,
                                  legend_name=legend_name,
                                  show=False).add_to(self.map)


        else:
            if geom == 'LineString':
                # Create a feature group
                layer = folium.FeatureGroup(name=legend_name, show=False)

                # Not null values
                for _, c in df.iterrows():
                    # add the line on the map
                    folium.PolyLine(c['points'], weight=color_weight, color = single_color).add_to(layer)
                # Add the layer to Map
                layer.add_to(self.map)

            if geom == 'Point':
                # Create a feature group
                layer = folium.FeatureGroup(name=legend_name, show=False)

                # Not null values
                for _, c in df.iterrows():
                    # add the line on the map
                    folium.CircleMarker(location = [c['points'][0][0], c['points'][0][1]], radius=marker_radius, color=single_color).add_to(layer)

                # Add the layer to Map
                layer.add_to(self.map)

            if geom == 'Polygon':
                # Not null values
                geo_data = gpd.GeoSeries(df.set_index(column_id)[column_geometry]).to_json()
                folium.Choropleth(geo_data=geo_data,
                                  name=legend_name,
                                  data=df,
                                  columns=[column_id, legend_name],
                                  key_on='feature.'+column_id,
                                  fill_color=single_color,
                                  fill_opacity=0.5,
                                  line_opacity=0.1,
                                  legend_name=legend_name,
                                  show=False).add_to(self.map)

    # Adding a legend method
    def add_categorical_legend(self, title=None):
        if title == None:
            title = input('Enter title for legend:')
        else:
            title = title
        legend_categories = ""
        for label, color in self.dic_colors.items():
            legend_categories += f"<li><span style='background:{color}'></span>{label}</li>"

        legend_html = f"""
        <div id='maplegend' class='maplegend'>
          <div class='legend-title'>{title}</div>
          <div class='legend-scale'>
            <ul class='legend-labels'>
            {legend_categories}
            </ul>
          </div>
        </div>
        """
        script = f"""
            <script type="text/javascript">
            var oneTimeExecution = (function() {{
                        var executed = false;
                        return function() {{
                            if (!executed) {{
                                 var checkExist = setInterval(function() {{
                                           if ((document.getElementsByClassName('leaflet-top leaflet-right').length) || (!executed)) {{
                                              document.getElementsByClassName('leaflet-top leaflet-right')[0].style.display = "flex"
                                              document.getElementsByClassName('leaflet-top leaflet-right')[0].style.flexDirection = "column"
                                              document.getElementsByClassName('leaflet-top leaflet-right')[0].innerHTML += `{legend_html}`;
                                              clearInterval(checkExist);
                                              executed = true;
                                           }}
                                        }}, 100);
                            }}
                        }};
                    }})();
            oneTimeExecution()
            </script>
          """


        css = """

        <style type='text/css'>
          .maplegend {
            z-index:9999;
            float:right;
            background-color: rgba(255, 255, 255, 1);
            border-radius: 5px;
            border: 2px solid #bbb;
            padding: 10px;
            font-size:12px;
            positon: relative;
          }
          .maplegend .legend-title {
            text-align: left;
            margin-bottom: 5px;
            font-weight: bold;
            font-size: 90%;
            }
          .maplegend .legend-scale ul {
            margin: 0;
            margin-bottom: 5px;
            padding: 0;
            float: left;
            list-style: none;
            }
          .maplegend .legend-scale ul li {
            font-size: 80%;
            list-style: none;
            margin-left: 0;
            line-height: 18px;
            margin-bottom: 2px;
            }
          .maplegend ul.legend-labels li span {
            display: block;
            float: left;
            height: 16px;
            width: 30px;
            margin-right: 5px;
            margin-left: 0;
            border: 0px solid #ccc;
            }
          .maplegend .legend-source {
            font-size: 80%;
            color: #777;
            clear: both;
            }
          .maplegend a {
            color: #777;
            }
        </style>
        """

        self.map.get_root().header.add_child(folium.Element(script + css))

    def show_or_save(self, option_show=False, option_save=False, map_name=None):
        """
        :param option_show: bool
            Defines the option whether to show map or not.
        :param option_save: bool
            Defines the option whether to save map or not.
        :param map_name: string
            Defines the name of the map.
        This method shows and saves the map in html format where it's been created
        """

        # Adding a LayerControl to map
        folium.LayerControl().add_to(self.map)

        # Option to display the map
        if option_show:
            display(self.map)

        # Option to save the map
        if option_save:
            if map_name == None:
                map_name = input('Enter name of map:')
            else:
                map_name = map_name
            # Saving the map
            self.map.save(map_name+'.html')
