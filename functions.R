# Functions for VISION 2050 Summary Work
sum_table_values <- function(tbl, w_col, w_scen, w_var, w_geo, w_yr) {
  
  wrk_tot <- as.integer(tbl[scenario %in% w_scen & variable %in%  w_var & get(w_col) %in% w_geo & year %in% w_yr,sum(value)])
  return(wrk_tot)
}

create_area_map <- function(geo_areas, w_directory) {
  
  # First start Base Map
  w_map <- leaflet() %>% addProviderTiles(providers$CartoDB.Positron, group="Base Map")
  list_of_layers <- NULL
  
  # Loop Over the List of Areas to Map and add as layers to the map
  for (areas in geo_areas) {
    w.shape <- readOGR(dsn=w_directory,layer=areas[[2]])
    w_map <- w_map %>%
      addPolygons(data=w.shape,
                  fillColor = areas[[1]],
                  color = areas[[1]],
                  fillOpacity = 0.7,
                  weight=1,
                  group=areas[[3]])
    if(is.null(list_of_layers)) {list_of_layers <- list(areas[[3]])} else {list_of_layers <- append(list_of_layers,areas[[3]])}
  }
  
  # Now Add Layer Controls and Easy Buttons
  w_map <- w_map %>%
    addLayersControl(baseGroups = c("Base Map"),
                     overlayGroups = list_of_layers,
                     options = layersControlOptions(collapsed = FALSE)) %>%
    addEasyButton(easyButton(
      icon="fa-anchor", title="Bremerton",
      onClick=JS("function(btn, map){  map.setView([47.565,-122.654],10.5); }"))) %>%
    addEasyButton(easyButton(
      icon="fa-amazon", title="Cross-Lake",
      onClick=JS("function(btn, map){  map.setView([47.615,-122.257],10.5); }"))) %>%
    addEasyButton(easyButton(
      icon="fa-plane", title="Everett",
      onClick=JS("function(btn, map){  map.setView([47.975,-122.196],10.5); }"))) %>%
    addEasyButton(easyButton(
      icon="fa-glass", title="Tacoma",
      onClick=JS("function(btn, map){  map.setView([47.252,-122.442],10.5); }"))) %>%
    addEasyButton(easyButton(
      icon="fa-globe", title="Region",
      onClick=JS("function(btn, map){  map.setView([47.615,-122.257],8.5); }")))
  
  return(w_map)
}

create_table_container <- function(cat_nms, scen_nms, metric_nms) {
  
  wrk_container = htmltools::withTags(table(
    class = 'display',
    thead(
      tr(
        th(class = 'dt-center', rowspan = 3, cat_nms)
      ),
      tr(
        lapply(scen_nms, function(x) th(class = 'dt-center', colspan =4, x))
      ),
      tr(
        lapply(rep(metric_nms, length(scen_nms)), function(x) th(class = 'dt-center', x))
      )
    )
  ))
  
  return(wrk_container)
  
}

create_station_area_tables <- function(tbl, alt_list,current_variable, tbl_view_len, w_type, w_digits) {
  
  short_names <- NULL
  for (files in alt_list) {
    short_names <- c(short_names, files[[1]])
  }
  
  scenario_names <- NULL
  for (files in alt_list) {
    scenario_names <- c(scenario_names, files[[3]])
  }
  
  # Create Variable Specific Table by Scenario
  wrk_summary <- tbl[variable %in% current_variable]
  wrk_summary[,variable:=NULL]
  
  s_tbl <- dcast(wrk_summary, station_name ~ scenario, value.var="results")
  setcolorder(s_tbl,c("station_name",short_names))
  
  clean_tbl <- datatable(s_tbl, rownames = FALSE, options = list(pageLength = tbl_view_len, columnDefs = list(list(className = 'dt-center', targets = 1:1))), colnames = c('Station Area', current_variable))
  
  for (working_column in short_names) {
    
    if (w_type == "integer") {
      clean_tbl <- clean_tbl %>% 
        formatCurrency(working_column, "", digits = w_digits) %>%
        formatStyle(working_column,`text-align` = 'center')
    } else {
      clean_tbl <- clean_tbl %>% 
        formatPercentage(working_column,w_digits) %>%
        formatStyle(working_column,`text-align` = 'center')
    }
    
  }
  
  return(clean_tbl)
}

create_rgc_tables <- function(tbl, alt_list,current_variable, tbl_view_len, w_type, w_digits) {
  
  short_names <- NULL
  for (files in alt_list) {
    short_names <- c(short_names, files[[1]])
  }
  
  scenario_names <- NULL
  for (files in alt_list) {
    scenario_names <- c(scenario_names, files[[3]])
  }
  
  # Create Variable Specific Table by Scenario
  wrk_summary <- tbl[variable %in% current_variable]
  wrk_summary[,variable:=NULL]
  
  s_tbl <- dcast(wrk_summary, rgc_name ~ scenario, value.var="results")
  setcolorder(s_tbl,c("rgc_name",short_names))
  
  clean_tbl <- datatable(s_tbl, rownames = FALSE, options = list(pageLength = tbl_view_len, columnDefs = list(list(className = 'dt-center', targets = 1:1))), colnames = c('Regional Growth Center', current_variable))
  
  for (working_column in short_names) {
    
    if (w_type == "integer") {
      clean_tbl <- clean_tbl %>% 
        formatCurrency(working_column, "", digits = w_digits) %>%
        formatStyle(working_column,`text-align` = 'center')
    } else {
      clean_tbl <- clean_tbl %>% 
        formatPercentage(working_column,w_digits) %>%
        formatStyle(working_column,`text-align` = 'center')
    }
    
  }
  
  return(clean_tbl)
}

create_table_from_input <- function(fdir,fname,ftype) {
  w_fname <- paste0(getwd(),"/",fdir,"/",fname,".",ftype)
  
  if (ftype == "tab" | ftype == "tsv" ) {wtbl <- read.table(w_fname, sep = '\t',header = TRUE)} 
  
  else if (ftype == "dbf") {wtbl <- read.dbf(w_fname)} 
  
  else  {wtbl <- read.csv(w_fname)}
  
  setDT(wtbl)
  return(wtbl)
}

create_bar_charts <- function(current_tbl, current_metric) {
  wrk_tbl <- current_tbl[variable %in% current_metric]
  ylimit <- max(wrk_tbl$value)
  setorder(wrk_tbl,value,value)
  
  labels <- paste0("<b>","Metro Area: ", "</b>",wrk_tbl$name,
                   "<b> <br>",paste0(current_metric,": "), "</b>",prettyNum(round(wrk_tbl$value, 0), big.mark = ",")) %>% lapply(htmltools::HTML)
  
  wrk_chart <- ggplot(wrk_tbl, aes(x = reorder(name,value), y= value, fill = as.factor(plot_id),text=labels)) + 
    geom_bar(stat = "identity") +
    theme_void() +
    scale_y_continuous(labels = comma)+
    scale_fill_manual(values=bar_colors)+
    theme(legend.position = "none",
          panel.grid.major = element_blank(),
          panel.grid.minor = element_blank(),
          panel.border = element_blank(),
          axis.line = element_blank())
  
  wrk_chart <- ggplotly(wrk_chart, tooltip = c("text"))
  return(wrk_chart)
}

calculate_rank <- function(current_tbl, current_metric, current_msa) {
  wrk_tbl <- current_tbl[variable %in% current_metric]
  wrk_tbl <- wrk_tbl[order(-value)]
  wrk_tbl$rank <- NA
  wrk_tbl$rank <- 1:nrow(wrk_tbl)
  
  wrk_rank <- wrk_tbl$rank[wrk_tbl$msa_id==current_msa]
  return(wrk_rank)
}

create_line_chart <- function(table,xcolumn, ycolumn, Items, ylimit, yname,  xname, wrk_title) {
  
  wrk_chart <- ggplot(table, aes(x = xcolumn, y= ycolumn, group= Items, colour= Items)) +
    geom_line(size=1) +
    scale_y_continuous(labels = comma, name = yname, limits = c(0, ylimit))+
    theme_light()+
    xlab(xname)+
    ggtitle(wrk_title)+
    theme(plot.title = element_text(family = "Trebuchet MS", color="#76787A", 
                                    size=16, 
                                    margin = margin(10, 0, 10, 0)),
          legend.position = "top",
          legend.title = element_blank(),
    )
  
  wrk_chart <- ggplotly(wrk_chart) %>% 
    layout(legend = list(orientation = "h", x = 1, xanchor = "center", y = -0.2))
  
  return(wrk_chart)
}

table_from_db <- function(srv_nm,db_nm,tbl_nm) {
  
  db_con <- dbConnect(odbc::odbc(),
                      driver = "SQL Server",
                      server = srv_nm,
                      database = db_nm,
                      trusted_connection = "yes"
  )
  
  w_tbl <- dbReadTable(db_con,SQL(tbl_nm))
  odbc::dbDisconnect(db_con)
  return(w_tbl)
}