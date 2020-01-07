import utils
import geoplot as gplt
import geopandas as gpd
from collections import Counter
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon

utils.update_source()  # by default it updates hotels
utils.update_source("provinces")

hnames, hcoords = utils.get_hotels_file()
pids, pnames, pcoords = utils.get_provinces_file()

hpids = [utils.state_by_coord(h, pids, pcoords) for h in hcoords]
hpoints = [Point(p) for p in hcoords]
hdensity = Counter(hpids)
hmax = hdensity.most_common(1)[0][1]

ppoly = [Polygon(p) for p in pcoords]
phdensity = [round(hdensity[p]*100/hmax, 0) for p in pids]

provinces_gdf = gpd.GeoDataFrame({
    'provinceid': pids,
    'provincename': pnames,
    'geometry': ppoly,
    'density': phdensity
})

hotels_gdf = gpd.GeoDataFrame({
    'hotelname': hnames,
    'geometry': hpoints,
})

gplt.choropleth(
    provinces_gdf,
    hue='density', cmap='Purples',
    projection=gplt.crs.AlbersEqualArea(),
    legend=True, legend_kwargs={'orientation': 'horizontal'}
)
plt.title("Hotel density by provinces in Armenia")
plt.savefig('hotels_density_by_provinces.png', bbox_inches='tight')

ax = gplt.kdeplot(
    hotels_gdf,
    clip=provinces_gdf.geometry,
    shade=True, shade_lowest=True,
    cmap='Reds', projection=gplt.crs.AlbersEqualArea()
)
gplt.polyplot(provinces_gdf, ax=ax, zorder=1)
plt.title("Hotels heatmap of Armenia")
plt.savefig('hotels_heatmap.png', bbox_inches='tight')