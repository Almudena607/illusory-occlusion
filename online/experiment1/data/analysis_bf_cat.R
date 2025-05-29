# Import libraries
library(dplyr)
library(readr)
library(stringr)
library(scales)
library(ggplot2)
library(ggdist)
library(tidyr)
library(BayesFactor)
# make sure data file and R file are saved in the same place
# set working directory to source file location (session > set working directory > to source file location)

####### PREPARING THE FILES ######

# Get a list of all CSV files in the directory
datapath <- list.files(pattern = "*.csv")

# Print the paths found to debug
print(datapath)

# Check if any files were found
if (length(datapath) == 0) {
  stop("No CSV files found in the specified directory.")
}

# Read all CSV files into a list of data frames
df <- lapply(datapath, function(file) {
  tryCatch({
    read_csv(file)
  }, error = function(e) {
    message(paste("Error reading file:", file))
    NULL
  })
})

# Check if any data frames were successfully read
if (length(df) == 0) {
  stop("No data frames could be created from the CSV files.")
}

# loop through all the files and correct the counterbalance
alldata <- data.frame()
s <- 0

for (f in datapath) {
  data <- read_csv(f)
  
  if (nrow(data) == 1092) {
    # Filter for rows where test_part is 'response'
    data <- data %>% filter(test_part == 'response')
    s <- s + 1
    
    # Ensure rt is numeric and handle non-numeric values
    data <- data %>%
      mutate(subjectnr = s,
             biological = ifelse(str_detect(stim, 'bio_'), 1, 0),
             behind = ifelse(str_detect(stim, '_behind_'), 'occluded', 'not occluded'),
             valid = ifelse(str_detect(stim, '_valid'), 'valid', 'invalid'),
             rt = as.numeric(rt))  # Convert rt to numeric
    
    # Check for NA values in rt
    if (any(is.na(data$rt))) {
      warning("NA values found in rt column, replacing with mean rt")
      data$rt[is.na(data$rt)] <- mean(data$rt, na.rm = TRUE)
    }
    
    # Determine the correct response
    c <- sapply(1:nrow(data), function(i) {
      if (str_detect(data$task[i], '\\[z\\] biological')) {
        if (data$biological[i] == 1) 'z' else 'm'
      } else {
        if (data$biological[i] == 1) 'm' else 'z'
      }
    })
    data$cresp <- c
    data$correct <- as.integer(data$response == data$cresp)
    data$zrt <- scale(data$rt)  # Calculate z-scores for rt
    
    alldata <- bind_rows(alldata, data)
  }
}

# Identify columns with list or matrix data
problematic_cols <- sapply(alldata, function(col) {
  is.list(col) || is.matrix(col)
})

# Print the names of problematic columns
print(names(alldata)[problematic_cols])

# Convert zrt matrix to a numeric vector
alldata$zrt <- as.numeric(alldata$zrt)

# Now write the cleaned data frame to CSV
write_csv(alldata, 'responses.csv')




####### AVERAGING CONDITIONS AND CALCULATING PERFORMANCE ######
# Define the path to your responses CSV file
responses_path <- "responses.csv"

# Read the data
Responses <- read_csv(responses_path)

# Get unique subject numbers
subjectnr <- unique(Responses$subjectnr)

# Initialize lists to store accuracy and reaction time data
acc_behval <- list()
acc_behinval <- list()
acc_frval <- list()
acc_frinval <- list()

rt_behval <- list()
rt_behinval <- list()
rt_frval <- list()
rt_frinval <- list()

ppt_df <- data.frame()
# Loop through each subject number
for (s in subjectnr) {
  # Initialize vectors for the current subject
  sacc_behval <- c()
  sacc_behinval <- c()
  sacc_frval <- c()
  sacc_frinval <- c()
  
  srt_behval <- c()
  srt_behinval <- c()
  srt_frval <- c()
  srt_frinval <- c()
  
  # Loop through the data to categorise accuracy and reaction time
  for (i in seq_len(nrow(Responses))) {
    if (Responses$subjectnr[i] == s) {
      x <- Responses$stim[i]
      if (grepl('behind_valid', x)) {
        sacc_behval <- c(sacc_behval, Responses$correct[i])
        srt_behval <- c(srt_behval, Responses$rt[i])
      } else if (grepl('behind_invalid', x)) {
        sacc_behinval <- c(sacc_behinval, Responses$correct[i])
        srt_behinval <- c(srt_behinval, Responses$rt[i])
      } else if (grepl('front_valid', x)) {
        sacc_frval <- c(sacc_frval, Responses$correct[i])
        srt_frval <- c(srt_frval, Responses$rt[i])
      } else if (grepl('front_invalid', x)) {
        sacc_frinval <- c(sacc_frinval, Responses$correct[i])
        srt_frinval <- c(srt_frinval, Responses$rt[i])
      }
    }
  }
  
  # Store the vectors for the current subject in the lists
  acc_behval[[as.character(s)]] <- mean(sacc_behval)
  acc_behinval[[as.character(s)]] <- mean(sacc_behinval)
  acc_frval[[as.character(s)]] <- mean(sacc_frval)
  acc_frinval[[as.character(s)]] <- mean(sacc_frinval)
  
  rt_behval[[as.character(s)]] <- mean(srt_behval)
  rt_behinval[[as.character(s)]] <- mean(srt_behinval)
  rt_frval[[as.character(s)]] <- mean(srt_frval)
  rt_frinval[[as.character(s)]] <- mean(srt_frinval)
  
  ppt_df <- data.frame(
    acc_behval = unlist(acc_behval),
    acc_behinval = unlist(acc_behinval),
    acc_frval = unlist(acc_frval),
    acc_frinval = unlist(acc_frinval),
    rt_behval = unlist(rt_behval),
    rt_behinval = unlist(rt_behinval),
    rt_frval = unlist(rt_frval),
    rt_frinval = unlist(rt_frinval),
    stringsAsFactors = FALSE
  )

}

# Define the function to calculate the performance index
calculate_performance_index <- function(accuracy, reaction_time) {
  # Convert reaction time to seconds if needed
  reaction_time_seconds <- reaction_time / 1000.0
  
  # Calculate composite performance index
  performance_index <- accuracy / reaction_time_seconds
  
  return(performance_index)
}

ppt_df$performance_behval <- mapply(calculate_performance_index, ppt_df$acc_behval, ppt_df$rt_behval)
ppt_df$performance_behinval <- mapply(calculate_performance_index, ppt_df$acc_behinval, ppt_df$rt_behinval)
ppt_df$performance_frval <- mapply(calculate_performance_index, ppt_df$acc_frval, ppt_df$rt_frval)
ppt_df$performance_frinval <- mapply(calculate_performance_index, ppt_df$acc_frinval, ppt_df$rt_frinval)

write.csv(ppt_df, "participants_performance.csv", row.names = TRUE)



# Create a data frame to store averages and differences
Avg <- data.frame(
  means_acc_behval = rowMeans(as.data.frame(acc_behval)),
  means_acc_behinval = rowMeans(as.data.frame(acc_behinval)),
  means_acc_frval = rowMeans(as.data.frame(acc_frval)),
  means_acc_frinval = rowMeans(as.data.frame(acc_frinval)),
  
  means_rt_behval = rowMeans(as.data.frame(rt_behval)),
  means_rt_behinval = rowMeans(as.data.frame(rt_behinval)),
  means_rt_frval = rowMeans(as.data.frame(rt_frval)),
  means_rt_frinval = rowMeans(as.data.frame(rt_frinval))
)

# Calculate differences
Avg$diff_acc_validity_behind <- Avg$means_acc_behval - Avg$means_acc_behinval
Avg$diff_acc_validity_front <- Avg$means_acc_frval - Avg$means_acc_frinval
Avg$diff_acc_position_valid <- Avg$means_acc_frval - Avg$means_acc_behval
Avg$diff_acc_position_invalid <- Avg$means_acc_frinval - Avg$means_acc_behinval

Avg$diff_rt_validity_behind <- Avg$means_rt_behval - Avg$means_rt_behinval
Avg$diff_rt_validity_front <- Avg$means_rt_frval - Avg$means_rt_frinval
Avg$diff_rt_position_valid <- Avg$means_rt_frval - Avg$means_rt_behval
Avg$diff_rt_position_invalid <- Avg$means_rt_frinval - Avg$means_rt_behinval

# Calculate performance indexes
Avg$performance_index_behval <- mapply(calculate_performance_index, Avg$means_acc_behval, Avg$means_rt_behval)
Avg$performance_index_behinval <- mapply(calculate_performance_index, Avg$means_acc_behinval, Avg$means_rt_behinval)
Avg$performance_index_frval <- mapply(calculate_performance_index, Avg$means_acc_frval, Avg$means_rt_frval)
Avg$performance_index_frinval <- mapply(calculate_performance_index, Avg$means_acc_frinval, Avg$means_rt_frinval)

# Calculate differences in performance indexes
Avg$performance_validity_behind <- Avg$performance_index_behval - Avg$performance_index_behinval
Avg$diff_performance_index_front <- Avg$performance_index_frval - Avg$performance_index_frinval

# Calculate control performance
Avg$control_performance <- (Avg$performance_index_frval + Avg$performance_index_frinval) - (Avg$performance_index_behval + Avg$performance_index_behinval)

# Write the data frame to a CSV file
write.csv(Avg, "averages_conditions_performance.csv", row.names = TRUE) 




###### T-TESTS AND BFS ######
### opening df from vs code -> 1: valid, 0: invalid

# df accuracy
#accuracy_clean <- read.csv('accuracies_clean.csv')
#acc_reshaped <- accuracy_clean %>%
#  filter(occlusion == 1) %>%
#  mutate(condition = ifelse(validity == 1, "acc_valid_occluded", "acc_invalid_occluded")) %>%
#  select(sub, condition, accuracy) %>%
#  pivot_wider(names_from = condition, values_from = accuracy)

# df rt
#rt_clean <- read.csv('rt_clean.csv')
#rt_reshaped <- rt_clean %>%
#  filter(occlusion == 1) %>%
#  mutate(condition = ifelse(validity == 1, "rt_valid_occluded", "rt_invalid_occluded")) %>%
#  select(sub, condition, rt_median) %>%
#  pivot_wider(names_from = condition, values_from = rt_median)


# df everything
averages_clean<- read.csv('averages_clean.csv')
averages_reshaped <- averages_clean %>%
  filter(occlusion == 1) %>%
  mutate(
    validity_condition = ifelse(validity == 1, "valid", "invalid")
  ) %>%
  select(sub, validity_condition, accuracy, rt) %>%
  pivot_wider(
    names_from = validity_condition,
    values_from = c(accuracy, rt),
    names_glue = "{.value}_{validity_condition}_occluded"
  )



### bayesian ttest
#averages_reshaped$diff_acc_validity <- averages_reshaped$accuracy_valid_occluded - averages_reshaped$accuracy_invalid_occluded
bf_acc <- ttestBF(x = averages_reshaped$accuracy_valid_occluded, y = averages_reshaped$accuracy_invalid_occluded,
                  nullInterval = c(-0.5,0.5), rscale = "medium", complement = TRUE)
acc_bf <- as.data.frame(bf_acc)


#averages_reshaped$diff_rt_validity <- averages_reshaped$rt_valid_occluded - averages_reshaped$rt_invalid_occluded
bf_rt <-  ttestBF(x = averages_reshaped$rt_valid_occluded, y = averages_reshaped$rt_invalid_occluded,
                  nullInterval = c(-0.5,0.5), rscale = "medium", complement = TRUE)
rt_bf <- as.data.frame(bf_rt)



bf <- data.frame(bf_accuracy = acc_bf$bf[1], error_accuracy = acc_bf$error[1], bf_rts = rt_bf$bf[1], error_rt = rt_bf$error[1])
write.csv(bf, 'bf-clean_data.csv', row.names = FALSE)


