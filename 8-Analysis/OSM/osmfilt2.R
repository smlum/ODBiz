# Packages
library(dplyr)
library(osmextract)
library(sf)

# Timing
totaltimestart <- Sys.time()

# Keys we're interested in
extratags <- c('leisure','sport','amenity','natural')

# Relating formatted names to two letter code for the other_relations DF
provdict <- c('alberta'='ab','british-columbia'='bc','manitoba'='mb',
              'new-brunswick'='nb','newfoundland-and-labrador'='nl',
              'nova-scotia'='ns','ontario'='on','prince-edward-island'='pe',
              'quebec'='qc','saskatchewan'='sk','northwest-territories'='nt',
              'nunavut'='nu','yukon'='yt')

osmfilt <- function(provterr,geomtype){
  # Query where at least one of the four keys needs a value
  osmquery <- paste("SELECT * FROM ",geomtype, " WHERE
               (leisure IS NOT NULL) OR (sport IS NOT NULL) OR
               (amenity IS NOT NULL) OR (natural IS NOT NULL)",sep='')
  nameFormat <- gsub(' ', '-', tolower(provterr))
  print(c(nameFormat,geomtype))
  osmURL <- paste("http://download.geofabrik.de/north-america/canada/",nameFormat,"-latest.osm.pbf",sep='')
  # Download, convert to GPKG, read in, only interested in certain columns
  provOSM <- oe_read(osmURL, layer = geomtype, extra_tags = extratags, query = osmquery,quiet=T) %>% 
    select(osm_id,name,leisure,sport,amenity,natural,other_tags,geometry)
  return(provOSM)
}

osmwrite <- function(provterr){
  nameFormat <- gsub(' ', '-', tolower(provterr))
  
  # Refer to previously made DF for other_relations (manually checked, only a few features)
  var <- paste(provdict[[nameFormat]],'Filt',sep='')
  provFilt <- get(var)
  
  # These are usually geometry collections so we're splitting by type
  provFiltLines <- st_collection_extract(provFilt,'LINESTRING')
  provFiltPoly <- st_collection_extract(provFilt,'POLYGON')
  filename <- paste(nameFormat,'.gpkg',sep='')
  
  # Get points and multipolygons from OSM
  osmPoints <- osmfilt(provterr,'points')
  osmMultiPoly <- osmfilt(provterr,'multipolygons')
  
  # Write to GPKG, overwrite layers
  st_write(osmPoints,filename,layer = paste('points-',nameFormat,sep=''),append=FALSE)
  st_write(provFiltLines,filename,layer=paste('linestrings-',nameFormat,sep=''),append=FALSE)
  st_write(provFiltPoly,filename,layer=paste('polygons-',nameFormat,sep=''),append=FALSE)
  st_write(osmMultiPoly,filename,layer = paste('multipolygons-',nameFormat,sep=''),append=FALSE)
}

# Each prov/terr, manually determined filter criteria
abOther <- osmfilt('alberta','other_relations')
abFilt <- abOther %>% filter(!is.na(leisure) | !is.na(amenity)) %>% 
  select(osm_id,name,leisure,sport,amenity,natural,other_tags,geometry)

bcOther <- osmfilt('british columbia','other_relations')
bcFilt <- bcOther %>% filter(!is.na(leisure)) %>% 
  select(osm_id,name,leisure,sport,amenity,natural,other_tags,geometry)

mbOther <- osmfilt('manitoba','other_relations')
mbFilt <- mbOther %>% filter(!is.na(leisure) & !is.na(amenity)) %>% 
  select(osm_id,name,leisure,sport,amenity,natural,other_tags,geometry)

nbOther <- osmfilt('new brunswick','other_relations')
nbFilt <- nbOther %>% filter(!is.na(leisure)) %>% 
  select(osm_id,name,leisure,sport,amenity,natural,other_tags,geometry)

nlOther <- osmfilt('newfoundland and labrador','other_relations')
nlFilt <- nlOther %>% filter(!is.na(leisure) | !is.na(amenity)) %>% 
  select(osm_id,name,leisure,sport,amenity,natural,other_tags,geometry)

nsOther <- osmfilt('nova scotia','other_relations')
nsFilt <- nsOther %>% filter(!is.na(leisure)) %>% 
  select(osm_id,name,leisure,sport,amenity,natural,other_tags,geometry)

onOther <- osmfilt('ontario','other_relations')
onFilt <- onOther %>% filter(leisure=='golf_course' | leisure=='marina' | amenity=='community_centre') %>% 
  select(osm_id,name,leisure,sport,amenity,natural,other_tags,geometry)

peOther <- osmfilt('prince edward island','other_relations')
peFilt <- peOther %>% filter(!is.na(leisure)) %>% 
  select(osm_id,name,leisure,sport,amenity,natural,other_tags,geometry)

qcOther <- osmfilt('quebec','other_relations')
qcFilt <- qcOther %>% filter(!is.na(leisure)) %>% 
  select(osm_id,name,leisure,sport,amenity,natural,other_tags,geometry)

skOther <- osmfilt('saskatchewan','other_relations')
skFilt <- skOther %>% filter(!is.na(leisure)) %>% 
  select(osm_id,name,leisure,sport,amenity,natural,other_tags,geometry)

ntOther <- osmfilt('northwest territories','other_relations')
ntFilt <- ntOther %>% filter(!is.na(leisure)) %>% 
  select(osm_id,name,leisure,sport,amenity,natural,other_tags,geometry)

nuOther <- osmfilt('nunavut','other_relations')
nuFilt <- nuOther %>% filter(!is.na(leisure)) %>% 
  select(osm_id,name,leisure,sport,amenity,natural,other_tags,geometry)

ytOther <- osmfilt('yukon','other_relations')
ytFilt <- ytOther %>% filter(!is.na(leisure)) %>% 
  select(osm_id,name,leisure,sport,amenity,natural,other_tags,geometry)

# Run and time for each prov/terr
ts <- Sys.time()
osmwrite('alberta')
te <- Sys.time()
print(te-ts)

ts <- Sys.time()
osmwrite('british columbia')
te <- Sys.time()
print(te-ts)

ts <- Sys.time()
osmwrite('manitoba')
te <- Sys.time()
print(te-ts)

ts <- Sys.time()
osmwrite('new brunswick')
te <- Sys.time()
print(te-ts)

ts <- Sys.time()
osmwrite('newfoundland and labrador')
te <- Sys.time()
print(te-ts)

ts <- Sys.time()
osmwrite('nova scotia')
te <- Sys.time()
print(te-ts)

ts <- Sys.time()
osmwrite('ontario')
te <- Sys.time()
print(te-ts)

ts <- Sys.time()
osmwrite('prince edward island')
te <- Sys.time()
print(te-ts)

ts <- Sys.time()
osmwrite('quebec')
te <- Sys.time()
print(te-ts)

ts <- Sys.time()
osmwrite('saskatchewan')
te <- Sys.time()
print(te-ts)

ts <- Sys.time()
osmwrite('northwest territories')
te <- Sys.time()
print(te-ts)

ts <- Sys.time()
osmwrite('nunavut')
te <- Sys.time()
print(te-ts)

ts <- Sys.time()
osmwrite('yukon')
te <- Sys.time()
print(te-ts)

totaltimeend <- Sys.time()
print('Done :)')
print(totaltimeend-totaltimestart)