#===============================================================================
# This file contains code snippets from  the paper "Who Leads? Who Follows? 
#           Measuring Issue Attention and Agenda Settingby Legislators and 
#           the Mass Public Using Social Media Data"
# originally published by: Pablo Barbera, Andreu Casas, Jonathan Nagler, Patrick J. Egan,
#           Richard Bonneau, John Jost, Joshua A. Tucker
# original code and data can be retrieved form here: https://doi.org/10.7910/DVN/AA96D2
# the original paper can be retrieved from here: doi: https://doi.org/10.1017/S0003055419000352
#
# the provided code has been adjusted and expanded to the need of this project 
# autocorrelation and stationary test have been written from scratch
#
#===============================================================================

# PACKAGES
#===============================================================================
library(dplyr)
library(xtable)
library(tidyr)
library(ggplot2)
library(urca)
library(vars)
library(boot)
library(rio)
library(boot)
library(RColorBrewer) 

#change the directory!
setwd("")

#===============================================================================
# First calculating some correlations
#===============================================================================
# DATA
#===============================================================================
db <- read.csv("Data\\time_data_count.csv")
#===============================================================================
# DATA without corona
#===============================================================================
db2 <- db %>%
  filter(topicName != 'corona')
#===============================================================================
# - calculate correlation between the agendas of each media outlet 
# - calculate the correlations for both datasets with and without corona
#===============================================================================

groups <- c( "spiegel", "welt", "sz", "zeit", "faz", "stern", "tagesschau")

results <- NULL
for (polgroup in groups) {
  new_col <- NULL
  for (compgroup in groups) {
    
    # - create a dataframe only with the two groups to compare
    comp_df <- data.frame(
      y = db[,polgroup],
      x = db[,compgroup]
    )
    
    comp_df2 <- data.frame(
      y = db2[,polgroup],
      x = db2[,compgroup]
    )
    
    # - remove NAs
    comp_df[is.na(comp_df)] <- 0
    comp_df2[is.na(comp_df2)] <- 0
    
    # - calculate correlation
    cor_out <- round(cor(comp_df)[2,1], 2)
    cor_out2 <- round(cor(comp_df2)[2,1], 2)
    
    new_cell <- data.frame(paste(cor_out,"(",cor_out2,")",sep = ""))
    print(new_cell)

    colnames(new_cell) <- polgroup
    rownames(new_cell) <- compgroup
    new_col <- rbind(new_col, new_cell)
  }
  if (is.null(results)) {
    results <- new_col
  } else {
    results <- cbind(results, new_col)
  }
}

#===============================================================================
# OUTPUT
#===============================================================================
# - adding human readable labels to the column and row names
rownames(results) <- c("Der Spiegel", "Die Welt", "Süddeutsche\nZeitung", "Die Zeit", "Frankfurter\nAllgemeine Zeitung", "Stern", "tagesschau")
colnames(results) <- c("Der Spiegel", "Die Welt", "Süddeutsche\nZeitung", "Die Zeit", "Frankfurter\nAllgemeine Zeitung", "Stern", "tagesschau")
xtable(results)
#===============================================================================
# Firstly creating a Plot on overall media agenda
#===============================================================================
dist <- read.csv("Data\\topic_distribution_overall.csv")
png("\\Figure\\Figure1.png", width = 400, height = 700)
ggplot(dist,
       aes(x = reorder(topicName,text)))+
  geom_bar(aes(weight = text))+
  coord_flip()+
  xlab("")+
  ylab("Number of Articles in the data")+
  theme_minimal()
dev.off()
#===============================================================================
# Secondly creating a Plot on publisher agenda
#===============================================================================
# - calculating the average by political issue and by group
db_long <- db %>%
  dplyr::select(topicName, groups) %>%
  gather(group, att, -topicName)

out_db <- db_long %>%
  group_by(group, topicName) %>%
  summarize(av = mean(att)) %>%
  as.data.frame()

# - provide readble labels to the groups
out_db$group <- recode(factor(out_db$group),
                       `spiegel` = "\nDer Spiegel",
                       `welt` = "\nDie Welt",
                       `sz` = "Süddeutsche\nZeitung",
                       `zeit` = "\nDie Zeit",
                       `faz` = "Frankfurter\nAllgemeine Zeitung",
                       `stern` = "\nStern",
                       `tagesschau` = "\nTagesschau")

# - re-level the group variable according to circulation
out_db$group <- factor(out_db$group,
                       levels = c(
                         "\nDer Spiegel",
                         "\nDie Welt",
                         "Süddeutsche\nZeitung",
                         "\nDie Zeit",
                         "Frankfurter\nAllgemeine Zeitung",
                         "\nStern",
                         "\nTagesschau"
                       ))

# - sort the labels in descending order by 'Der Spiegel' landing page placements
out_db <- out_db %>%
  arrange(group, av)

out_db$topicName <- factor(out_db$topicName, levels = unique(out_db$topicName))

#===============================================================================
# OUTPUT -- FIGURE
#===============================================================================
png("\\Figure\\Figure2.png", width = 2200, height = 3200)
ggplot(out_db, 
       aes(x = topicName, y = av)) +
  geom_bar(stat = "identity", position = "dodge", alpha = 0.8) +
  facet_wrap(~ group, nrow = 1) +
  scale_y_sqrt() +
  ylab("\nAverage number of articles for each topic in the top 20 articles") +
  coord_flip() +
  theme(panel.background = element_blank(),
        strip.text = element_text(size = 28),
        axis.text.y = element_text(size = 22),
        axis.text.x = element_text(size = 18),
        axis.title.x = element_text(size = 30),
        axis.title.y = element_text(size=0),
        panel.grid.major.x = element_line(color = "black"),
        panel.grid.major.y = element_line(color = "gray50"))
dev.off()


#===============================================================================
# TEST - Autocorrelation
#===============================================================================
variables <- c( "spiegel", "welt", "sz", "zeit", "faz", "stern", "tagesschau")
db <- read.csv("\\Data\\time_data_percent.csv")


counter <-0
listoflags <- vector(length=51) #initialize vector for ac values

#calculate autocorrelation and add it up. increment counter to calculate mean
for (top in unique(db$topicName)){
  for (var in variables){
    maindb <- db %>%
      filter(topicName == top)
    
    test <- acf(maindb[,var], lag.max=50, plot = FALSE)
    stats <- test[[1]]
    stats[is.na(stats)] <- 0
    
    listoflags <- listoflags + stats
    counter <- counter + 1
  }
}
#get mean
listoflags <- listoflags/counter

#create df
auto_df <- data.frame(autocorrelation = listoflags, hours = c(seq(1,51)))
auto_df
#autocorrelation drops below 0.1 in the average after 26 hours
png("\\Figure\\Figure3.png", width = 2200, height = 3200)
ggplot(data=auto_df,aes(x=hours, y=autocorrelation, group=1)) +
  geom_line()+
  geom_point()+
  theme_classic()+
  scale_y_continuous(expand = c(0, 0), limits = c(0, 1))+ 
  geom_hline(yintercept=0.1, color="red")
dev.off()

#===============================================================================
# TEST - Stationary
#===============================================================================
#init all the values
testvalue=NULL
topics=NULL
pub=NULL
critvalue5=NULL
critvalue10=NULL
nlags=NULL
stationary=NULL

#test stationarity and save values
for (top in unique(db$topicName)) {
  for (var in variables){
    
    maindb <- db %>%
      filter(topicName == top)
    test = ur.df(maindb[,var]+0.01, lags = 26) 
    critvalue5 <- rbind(critvalue5,test@cval[1,2])
    critvalue10 <- rbind(critvalue10,test@cval[1,3])
    testvalue <- rbind(testvalue,test@teststat[1,1])
    topics <- rbind(topics,top)
    pub <- rbind(pub,var)
    nlags <- rbind(nlags,test@lags)
  }
}
#combine in dataframe
stationary <- cbind(nlags,testvalue,topics,pub,critvalue5,critvalue10)
stationary <- data.frame(stationary)

#dummy variable for stationarity
stationary$stat5 <- with(stationary, testvalue < critvalue5)
stationary$stat10 <- with(stationary, testvalue < critvalue10)

#rename columns and rows
names(stationary) <- c("Lags", "TestStat", "Topic","Publisher","CritVal5","CritVal10","Stat5","Stat10")
rownames(stationary) <- NULL

#get nonstationary topics
nonstationary <- rbind(subset(stationary,Stat10==FALSE),subset(stationary,is.na(Stat10)))
rownames(nonstationary) <- NULL
nonstationary <- unique(nonstationary$Topic)

#remove topics with nonstationary series
for (nontop in nonstationary){
  db <- db %>%
    filter(topicName != nontop)
}
#write stationary topics to dataset
write.csv(db, "\\Data\\time_data_percent_stationary.csv")

#===============================================================================
# Calculate the VAR Model
#===============================================================================
variables <- c( "spiegel", "welt", "sz", "zeit", "faz", "stern", "tagesschau")


# - logit transform all series
for (v in variables) {
  # - pulling the series-agenda for that group
  x <- db[,v]
  # - get rid of NAs and removing a 1, as the log will generate NAs otherwise
  x[which(is.na(x))] <-0
  x[which(x==1)] <-0.98
  # - adding 1 percentage point to avoid 0s before the logit transformation
  x <- x + 0.01
  # - applying the non-linear transformation
  logit_x <- log(x / (1-x))
  db[,v] <- logit_x
}

# - adding "topic" to the list of model variables
variables <- c(variables, "topicName")

maindb <- db

# - a formula object that will facilitate transforming the topic variable from
#     factor to dummies
maindb$topicName <- as.character(maindb$topicName)
mformula <- formula(paste0("~", 
                           paste0(variables, collapse = " + ")))
model_data <- model.matrix(mformula, maindb[, variables])
model_data <- model_data[, 2:ncol(model_data)] # removing intercept

# - splitting the covariates of interest from the issue dummy variables
X_endogenous <- model_data[, which(!grepl("topicName", colnames(model_data)))]
X_exogenous <- model_data[, which(grepl("topicName", colnames(model_data)))]

# - estimating the model: 26 Lags 
var_model_merged <- VAR(y = X_endogenous, p=26, exogen = X_exogenous)

# calculating IRFs
var_irfs_cum_merged <- irf(var_model_merged, n.ahead = 60, cumulative = TRUE)

# - saving the VAR model
save(var_model_merged, file = "C:\\Users\\fabia\\Documents\\GitHub\\Scraping\\ProcessedData\\final\\model\\var_model_nonstat-MAIN.Rdata")

# - saving the IRFs
save(var_irfs_cum_merged, file = "C:\\Users\\fabia\\Documents\\GitHub\\Scraping\\ProcessedData\\final\\model\\var_irfs_nonstat-MAIN.Rdata")


#===============================================================================
# Calculate the IRF Effects after 30 days
#===============================================================================

var_irfs <- var_irfs_cum_merged
variables <- c( "spiegel", "welt", "sz", "zeit", "faz", "stern", "tagesschau")

# - a list with the elements of interest from the IRF object
elements_to_pull <- c("irf", "Upper", "Lower")

# - initializing and filling a dataset with the IRF info
irf_data <- NULL
for (el in elements_to_pull) {
  new_irf_info <- var_irfs[el][[1]]
  for (out in variables) {
    new_irf_var_data <- as.data.frame(new_irf_info[out][[1]])
    
    # - take inverse logit to transform the effects to percentage point changes
    new_irf_var_data_transf <- as.data.frame(
      sapply(1:ncol(new_irf_var_data), function(j)
        (inv.logit(new_irf_var_data[,j])-0.5)))
    colnames(new_irf_var_data_transf) <- colnames(new_irf_var_data)
    new_irf_var_data_long <- new_irf_var_data_transf %>%
      gather(cov, value)
    new_irf_var_data_long$out <- out
    new_irf_var_data_long$hour <- rep(1:nrow(new_irf_var_data), 
                                      length(unique(new_irf_var_data_long$cov)))
    new_irf_var_data_long$e_type <- el
    irf_data <- rbind(irf_data, new_irf_var_data_long)
  }
}

# - give easier labels to the estimate types (e.g. Lower --> lwr)
irf_data$e_type <- recode(irf_data$e_type,
                          `irf` = "pe",
                          `Lower` = "lwr", 
                          `Upper` = "upr")

# - initializing a output dataset 
new_irf_data <- NULL

# - a vector with the name of the variables
variables <- c( "spiegel", "welt", "sz", "zeit", "faz", "stern", "tagesschau")

# - deciding the number of hours to simulate
HOURS <- 60

irf_data <- irf_data %>%
  filter(hour <= (HOURS + 1))

# - iterating through covariates
for (covariate in variables) {
  # -iterating through outcomes
  for (outcome in variables) {
    # - skipping when covariate and response are the same
    if (covariate != outcome) {
      # - initializing a cummulative-shocks matrix for this scenario: two 3-dim 
      #     matrix, one matrix for the covariate and one matrix for the response,
      #     and one dimension for the point estimate and the two other dimensions
      #     for the lower and upper bounds of the estimate
      cov_mat <- array(0, dim = c(HOURS, HOURS, 3))
      out_mat <- array(0, dim = c(HOURS, HOURS, 3))
      
      # - pull the full 30-hour IRFs for the endogenous covariate
      cov_resp <- irf_data %>%
        filter(cov == covariate, out == covariate) %>%
        # - remove 1st row: it's part of the set-up (repsonse at hour 0)
        filter(hour != 1) %>%
        mutate(hour = hour -1)
      
      # - pull the full 30-hour IRFs for the particular outcome variable
      out_resp <- irf_data %>%
        filter(cov == covariate, out == outcome) %>%
        # - remove 1st row: it's part of the set-up (repsonse at hour 0)
        filter(hour != 1) %>%
        mutate(hour = hour -1)
      
      # - transforming the 30-hour IRFs for the covariate and outcome to a wide
      #   3-column format (one column per estimate type: pe, lwr, upr)
      or_cov_resp <- cov_resp %>%
        dplyr::select(hour, value, e_type) %>%
        spread(e_type, value) %>%
        dplyr::select(-hour)
      
      or_out_resp <- out_resp %>%
        dplyr::select(hour, value, e_type) %>%
        spread(e_type, value) %>%
        dplyr::select(-hour)
      
      # - fill up the first rows of the scenario matrices with the original 
      #   1-hour shock responses
      cov_mat[1,,1:3] <- or_cov_resp %>%
        as.matrix()
      out_mat[1,,1:3] <- or_out_resp %>%
        as.matrix()
      
      for (i in 2:HOURS) {
        # - iterating through the rest of the 30 hours, beyond the 1st one
        # - checking first how much attention the covariate group is predicted 
        #   to pay to the issue in hour i-1
        cov_att_pe <- sum(cov_mat[,(i-1),2])
        
        # - calculating how big a new shock needs to be in order for the 
        #   covariate group to keep its attention to 100%
        cov_new_shock <- 1 - cov_att_pe
        
        # - re-scaling the original 100 percentage point shock to the new shock
        cov_new_resp <- or_cov_resp[1:(HOURS-(i-1)),] * cov_new_shock
        out_new_resp <- or_out_resp[1:(HOURS-(i-1)),] * cov_new_shock
        
        # - adding the response to this new shock to the scenario matrices
        cov_mat[i,i:HOURS,1:3] <- cov_new_resp %>%
          as.matrix()
        out_mat[i,i:HOURS,1:3] <- out_new_resp %>%
          as.matrix()
      }
      # - saving the output for this cov --> out 
      new_rows <- rbind(
        data.frame(
          cov = covariate,
          value = colSums(out_mat[,,1]),
          out = outcome,
          hour = 1:HOURS,
          e_type = "lwr",
          data_type = "structural"),
        data.frame(
          cov = covariate,
          value = colSums(out_mat[,,2]),
          out = outcome,
          hour = 1:HOURS,
          e_type = "pe",
          data_type = "structural"),
        data.frame(
          cov = covariate,
          value = colSums(out_mat[,,3]),
          out = outcome,
          hour = 1:HOURS,
          e_type = "upr",
          data_type = "structural")
      )
      new_irf_data <- rbind(new_irf_data, new_rows)
    }
  }
}


# - merging this new type of IRFs with the "regular" 1-time-shock IRFs
irf_data$data_type <- "one_time_shock"
irf_data <- irf_data %>%
  # - correct the original data for the fact that hour 1 is just pre-setting
  filter(hour != 1) %>% 
  mutate(hour = hour -1)

all_irf_data <- rbind(irf_data, new_irf_data)

# - removing from the dataset cases in which covariate and outcome are the same
all_irf_data <- all_irf_data %>%
  filter(cov != out)

# - a wide version of the dataset, with a separate column for each estimate type
all_irf_data_wide <- all_irf_data %>%
  spread(e_type, value)

# - simulate one-time and structural shocks of 10 instead of 100 percentage pts.
#   Present the results in 0-20 scale instead of 0-1 according to number of articles
all_irf_data_wide <- all_irf_data %>%
  mutate(value = (value / 10) * 20) %>%
  spread(e_type, value)


# - human readble labels for the covariates and outcomes
all_irf_data_wide$cov <- recode(factor(all_irf_data_wide$cov),
                                `spiegel` = "\nDer Spiegel",
                                `welt` = "\nDie Welt",
                                `sz` = "Süddeutsche\nZeitung",
                                `zeit` = "\nDie Zeit",
                                `faz` = "Frankfurter\nAllgemeine Zeitung",
                                `stern` = "\nStern",
                                `tagesschau` = "\nTagesschau")

all_irf_data_wide$out <- recode(factor(all_irf_data_wide$out),
                                `spiegel` = "\nDer Spiegel",
                                `welt` = "\nDie Welt",
                                `sz` = "Süddeutsche\nZeitung",
                                `zeit` = "\nDie Zeit",
                                `faz` = "Frankfurter\nAllgemeine Zeitung",
                                `stern` = "\nStern",
                                `tagesschau` = "\nTagesschau")

# - reorder the levels of the outcome and covariate factor variables
all_irf_data_wide$out <- factor(all_irf_data_wide$out,
                                levels = c(
                                  "\nDer Spiegel",
                                  "\nDie Welt",
                                  "Süddeutsche\nZeitung",
                                  "\nDie Zeit",
                                  "Frankfurter\nAllgemeine Zeitung",
                                  "\nStern",
                                  "\nTagesschau"
                                ))

all_irf_data_wide$cov <- factor(all_irf_data_wide$cov,
                                levels = c(
                                  "\nDer Spiegel",
                                  "\nDie Welt",
                                  "Süddeutsche\nZeitung",
                                  "\nDie Zeit",
                                  "Frankfurter\nAllgemeine Zeitung",
                                  "\nStern",
                                  "\nTagesschau"
                                ))

# - better labels for the data type
all_irf_data_wide$data_type <- recode(
  all_irf_data_wide$data_type,
  `one_time_shock` =  "Effect of a one time 2 article increase at hour 0",
  `structural` = "Effect of a structural 2 article point attention increase at hour 0")

#saving results of the 30-hour effects
write.csv(all_irf_data_wide,"\\model\\onetime-structural-shock-irfs-results.csv",
          row.names = FALSE)

#===============================================================================
#Create Figure 4
#===============================================================================

final_input <- all_irf_data_wide

# - exploring only 30-hour effects
plot_db <- final_input %>%
  filter(hour == 30)

# - re-phrase the shock labels
plot_db$data_type <- ifelse(
  grepl("one time", plot_db$data_type),
  "The effect of a one time 2 article increase in hour 0             ",
  "The effect of a permanent 2 article increase in hour 0"
)

png("\\Figure\\figure4.png", width = 1600, height = 700)
ggplot(plot_db,
       aes(x = cov, y = pe, ymin = lwr, ymax = upr, col = data_type)) +
  geom_segment(aes(x = cov, xend = cov, y = lwr, yend = upr), 
               size = 2.5) +
  facet_wrap(~ out, nrow = 1) +
  coord_flip() +
  xlab("") +
  ylab("") +
  scale_color_manual("",values = c("gray60", "gray10")) +
  theme(
    panel.spacing = unit(1.05, "lines"),
    legend.position = "bottom",
    panel.background = element_blank(),
    panel.grid.major = element_line(colour = "gray90", linetype = "solid"),
    axis.text = element_text(size = 18),
    axis.text.y = element_text(hjust=0),
    strip.text = element_text(size = 20),
    panel.border = element_rect(colour = "black", fill = FALSE),
    strip.background = element_rect(colour = "black"),
    axis.title = element_text(size = 16),
    legend.text = element_text(size = 16)
  )
dev.off()

#===============================================================================
#Create Figure 6 (an inverse of Figure 4 - swaping cov and out)
#===============================================================================

png("C:\\Users\\fabia\\Documents\\GitHub\\Scraping\\ProcessedData\\final\\Figure\\figure2_reversed.png", width = 1600, height = 700)
ggplot(plot_db,
       aes(x = out, y = pe, ymin = lwr, ymax = upr, col = data_type)) +
  geom_segment(aes(x = out, xend = out, y = lwr, yend = upr), 
               size = 2.5) +
  facet_wrap(~ cov, nrow = 1) +
  coord_flip() +
  xlab("") +
  ylab("") +
  scale_color_manual("",values = c("gray60", "gray10")) +
  theme(
    panel.spacing = unit(1.05, "lines"),
    legend.position = "bottom",
    panel.background = element_blank(),
    panel.grid.major = element_line(colour = "gray90", linetype = "solid"),
    axis.text = element_text(size = 18),
    axis.text.y = element_text(hjust=0),
    strip.text = element_text(size = 20),
    panel.border = element_rect(colour = "black", fill = FALSE),
    strip.background = element_rect(colour = "black"),
    axis.title = element_text(size = 16),
    legend.text = element_text(size = 16)
  )
dev.off()


#===============================================================================
# Calculate VAR Model and IRFs without topic-fixed effects
#===============================================================================
#read db again
db <- read.csv("\\Data\\time_data_percent_stationary.csv")

#set variables of interest
variables <- c("faz","spiegel","stern","sz","tagesschau","welt","zeit")

# - selecting only the variables of interest 
db <- db[, c("time", "topicName", variables)]

# - logit transform all series
for (v in variables) {
  # - pulling the series-agenda for that group
  x <- db[,v]
  # - get rid of NAs and removing a 1, as the log will generate NAs otherwise
  x[which(is.na(x))] <-0 
  x[which(x==1)] <-0.98 
  # - adding 1 percentage point to avoid 0s before the logit transformation
  x <- x + 0.01
  # - applying the non-linear transformation
  logit_x <- log(x / (1-x))
  db[,v] <- logit_x
}

#calculate VAR and IRF
for (top in unique(db$topicName)) {
  maindb <- db %>%
    filter(topicName == top)
  # - data to matrix
  mformula <- formula(paste0("~", 
                             paste0(variables, collapse = " + ")))
  model_data <- model.matrix(mformula, maindb[, variables])
  model_data <- model_data[, 2:ncol(model_data)] # removing intercept
  
  # - only fitting endogenous variable in this case, no topic dummies
  X_endogenous <- model_data
  
  # - estimating the model, 26 lags of each endogenous variable
  var_model <- VAR(y = X_endogenous, p = 26)
  
  # - calculating cummulative 15 hour IRFs
  var_irfs_cum <- irf(var_model, n.ahead = 60, cumulative = TRUE)
  
  # OUTPUT
  #=============================================================================
  save(var_irfs_cum, 
       file = paste0("\\model\\var_irfs_topic_", top, "_logit-UPD.Rdata"))
}


#===============================================================================
#Create Figure 5
#===============================================================================

# - a list with variables of interest
variables <- c("faz","spiegel","stern","sz","tagesschau","welt","zeit")

# - initializing an empty dataset where to put all IRF info by topic
irf_data <- NULL

total <- length(unique(db$topicName))
counter <- 0
for (top in unique(db$topicName)) {
  # - update counter and report progress
  counter <- counter + 1
  print(paste0("[", counter, "/", total, "]"))
  
  #load each irf 
  file_name <- paste0("\\model\\var_irfs_topic_", top, "_logit-UPD.Rdata")
  load(file_name) # object name: 'var_irfs_cum'
  
  # - iterating through endogenous covariates and endogenous responses
  covs <- resps <- names(var_irfs_cum$irf)
  for (covariate in covs) {
    for (response in resps) {
      cum_hours_n <- nrow(var_irfs_cum$irf[[covariate]])
      new_rows <- data.frame(
        topicName = top,
        cov = rep(covariate, cum_hours_n),
        out = response,
        hour = 1:cum_hours_n,
        pe = NA, lwr = NA, upr = NA
      )
      
      # - iterating through estimate info (point estimate and lwr and upr CIs)
      for (estimate in c("irf", "Lower", "Upper")) {
        cov_irf_est <- as.data.frame(
          var_irfs_cum[[estimate]][[covariate]]
        )[[response]]
        # - inverting the logit transformation
        if (estimate == "irf") {
          new_rows$pe <- inv.logit(cov_irf_est) - 0.5 
        } else if (estimate == "Lower") {
          new_rows$lwr <- inv.logit(cov_irf_est) - 0.5
        } else {
          new_rows$upr <- inv.logit(cov_irf_est) - 0.5
        }
      }
      # - appending new rows to the main dataset with all IRF info
      irf_data <- rbind(irf_data, new_rows)
    }
  }
}


irf_plot <- irf_data 
# - removing rows where covariate and response are the same variable
agenda_type <- data.frame(
  var = c("faz","spiegel","stern","sz","tagesschau","welt","zeit"),
  type = c("faz","spiegel","stern","sz","tagesschau","welt","zeit")
)
cov_agenda_type <- agenda_type %>%
  rename(cov = var, cov_agenda_type = type)
out_agenda_type <- agenda_type %>%
  rename(out = var, out_agenda_type = type)

cov_agenda_type$cov <- as.character(cov_agenda_type$cov)
out_agenda_type$out <- as.character(out_agenda_type$out)
irf_plot$cov <- as.character(irf_plot$cov)
irf_plot$out <- as.character(irf_plot$out)

irf_plot <- left_join(irf_plot, cov_agenda_type)
irf_plot <- left_join(irf_plot, out_agenda_type)

irf_plot <- irf_plot %>%
  filter(cov_agenda_type != out_agenda_type)

irf_plot$topicName <- as.character(irf_plot$topicName)

# - providing better labels to the outcome and response variables
irf_plot$out <- recode(irf_plot$out,
                       `spiegel` = "\nDer Spiegel",
                       `welt` = "\nDie Welt",
                       `sz` = "Süddeutsche\nZeitung",
                       `zeit` = "\nDie Zeit",
                       `faz` = "Frankfurter\nAllgemeine Zeitung",
                       `stern` = "\nStern",
                       `tagesschau` = "\nTagesschau")

irf_plot$cov <- recode(irf_plot$cov,
                       `spiegel` = "\nDer Spiegel",
                       `welt` = "\nDie Welt",
                       `sz` = "Süddeutsche\nZeitung",
                       `zeit` = "\nDie Zeit",
                       `faz` = "Frankfurter\nAllgemeine Zeitung",
                       `stern` = "\nStern",
                       `tagesschau` = "\nTagesschau")


# - relevel these variables
irf_plot$out <- factor(irf_plot$out,
                       levels = c(
                         "\nDer Spiegel",
                         "\nDie Welt",
                         "Süddeutsche\nZeitung",
                         "\nDie Zeit",
                         "Frankfurter\nAllgemeine Zeitung",
                         "\nStern",
                         "\nTagesschau"
                       ))

irf_plot$cov <- factor(irf_plot$cov,
                       levels = c(
                         "\nDer Spiegel",
                         "\nDie Welt",
                         "Süddeutsche\nZeitung",
                         "\nDie Zeit",
                         "Frankfurter\nAllgemeine Zeitung",
                         "\nStern",
                         "\nTagesschau"
                       ))

# - excluding the IRFs that cross 0 
plot_db <- irf_plot %>%
  # - only keeping IRF that don't cross 0
  filter(hour == 30) %>%
  arrange(out, cov, pe) %>%
  mutate(label = factor(topicName, levels = unique(topicName))) %>%
  filter(sign(lwr) == sign(upr))

#plot and save to file
png("\\Figure\\figure4.png", width = 1600, height = 600)
ggplot(plot_db %>% 
         mutate(pe = (pe * 20)/10, lwr = (lwr * 20)/10, upr = (upr * 20)/10),
       aes(x = topicName, y = pe, ymin = lwr, ymax = upr)) +
  geom_pointrange(aes(col = cov), alpha = 0.2, size = 1.2) +
  geom_hline(yintercept = 0, color = "red3") +
  facet_wrap(~out, nrow = 1) +
  coord_flip() +
  xlab("") +
  ylab("\nThe effect of a 2 article increase on the landing page by the covariate group, measured in article placement change") +
  scale_color_brewer(palette = "Dark2")+
  theme(
    panel.background = element_blank(),
    panel.grid.major = element_line(colour = "gray90", linetype = "solid"),
    axis.text.x = element_text(size = 16),
    axis.text.y = element_text(size = 16),
    strip.text = element_text(size = 16),
    panel.border = element_rect(colour = "black", fill = FALSE),
    strip.background = element_rect(colour = "black"),
    axis.title = element_text(size = 14),
    legend.text = element_text(size = 14, margin = margin(t = 20), vjust = 5),
    legend.title = element_text(size=0)
  )
dev.off()
