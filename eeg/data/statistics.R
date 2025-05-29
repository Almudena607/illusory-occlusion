# libraries and datapath
library(ggplot2)
library(gridExtra)
library(grid)
library(dplyr)
library(stringr)
library(BayesFactor)
library(zoo)

datapath <- file.path("/illusory-occlusion/eeg/data")

posval_codes <- list(
  "_front_valid_" = "frval",
  "_front_invalid_" = "frinval",
  "_behind_valid_" = "behval",
  "_behind_invalid_" = "behinval"
)



### BAYES FACTORS CONTROL CONDITIONS ####

chance_level <- 0.5 
sub_val <- file.path(datapath, "derivatives/results_control/stats/subjects_control.csv") #smoothed -> done in python
if (file.exists(sub_val)) {
  all_data_validity <- read.csv(sub_val)
  print(head(all_data_validity))  # Debug
} else {
  stop("File not found: ", sub_val)
}

all_data_validity_diff <- all_data_validity - chance_level

n_timepoints <- nrow(all_data_validity_diff)

b_factors <- numeric(n_timepoints)
# Loop over each time point (rows)
for (t in 1:n_timepoints) {
  time_point_data <- as.numeric(all_data_validity_diff[t, ])  # Extract all participants for time point `t`
  time_point_data <- time_point_data[!is.na(time_point_data)]
  
  if (length(time_point_data) > 1) {
    results <- ttestBF(x = time_point_data, mu = 0, nullInterval = c(0.5,Inf), rscale = "medium")
    
    print(results)

    b_factors[t] <- results
  } 
}


b_factors_df <- data.frame(Bayes_Factor = b_factors)
output_bf_2 <- file.path(datapath, 'derivatives/results_control/stats/bf_validity_diff.csv')
write.csv(b_factors_df, output_bf_2, row.names = FALSE)




#### BAYES FACTORS MAIN ####


list_levels <- c('supraordinate', 'category', 'object', 'image')
all_data <- list()
for (c in names(posval_codes)) {
  for (j in 0:49) {
    subjectnr <- sprintf('%02d', j)
    infn <- file.path(datapath, "derivatives/results_main", paste0("sub-", subjectnr, "_results_", posval_codes[[c]], "_im.csv"))
    
    if (file.exists(infn)) {
      DF <- read.csv(infn)
      time <- DF$time
      
      for (level in colnames(DF)) {
        if (level %in% list_levels) {
          key <- paste0(subjectnr, c, level)
          all_data[[key]] <- DF[[level]]
        }
      }
    }
  }
}
DF <- as.data.frame(all_data)
DF$time <- time
output <- file.path(datapath, 'derivatives/results_main/alldata.csv')
write.csv(DF, output, row.names = FALSE)



n_timepoints <- length(time)

#column names
pattern <- "X(\\d\\d)_((\\w+)_(\\w+)_(\\w+))"

# data from all participants for each condition
condition_list <- list()
for (col in colnames(DF)) {
  match <- regmatches(col, regexec(pattern, col))
  if (length(match[[1]]) > 1) {
    condition <- match[[1]][2]
    
    if (!condition %in% names(condition_list)) {
      condition_list[[condition]] <- data.frame(row.names = time)
    }
    
    condition_list[[condition]][[col]] <- DF[[col]]
  }
}


 



# Re-structure the df
levels <- c('supraordinate', 'category', 'object', 'image')
positions <- c('front', 'behind')
validity<- c('valid', 'invalid')


valid_x <- list()
invalid_y <- list()
for (j in 0:31) {
  subjectnr <- sprintf('%02d', j)
  
  # Skip if subject doesn't exist in condition_list
  if (!subjectnr %in% names(condition_list)){
    print(subjectnr)
  }
  
  for (lev in levels) {
    for (val in validity) {
        # Create all key variants
        val_key <- paste0("X", subjectnr, "_behind_valid_", lev)
        inval_key <- paste0("X", subjectnr, "_behind_invalid_", lev)
        
        key <- paste0(lev)

        if (!key %in% names(valid_x)) {
          valid_x[[key]] <- data.frame(row.names = time)
        }
        
        if (!key %in% names(invalid_y)) {
          invalid_y[[key]] <- data.frame(row.names = time)
        }
        
        if (val_key %in% names(condition_list[[subjectnr]])) {
          valid_x[[key]][[subjectnr]]<- condition_list[[subjectnr]][[val_key]]
        }
        
        if (inval_key %in% names(condition_list[[subjectnr]])) {
          invalid_y[[key]][[subjectnr]] <- condition_list[[subjectnr]][[inval_key]]
      }
    }
  }
}

valid_x_df <- as.data.frame(valid_x)
invalid_y_df <- as.data.frame(invalid_y)





# Hardcoding objects and supraordinate for full-cauchy
object_bf2 <- list()
### hardcoding objects
df_valid <- as.data.frame(valid_x[['object']])
df_invalid <- as.data.frame(invalid_y[['object']])
b_factors <- rep(NA_real_, n_timepoints)
for (t in 1:n_timepoints) {
  timepoint_value_valid <- na.omit(as.numeric(df_valid[t, ]))
  timepoint_value_invalid <- na.omit(as.numeric(df_invalid[t, ]))
  
  if (length(timepoint_value_valid) > 1) {
    tryCatch({
      
      results <- ttestBF(
        x = timepoint_value_valid,
        y = timepoint_value_invalid,
        nullInterval = c(-0.5, 0.5),
        paired = TRUE,
        rscale = "medium",
        complement = TRUE
      )
      print(results)
      b_factors[t] <- extractBF(results)[2, "bf"] # 2 is the complement
      
    }, error = function(e) {
      message("Error calculating BF for ", 'object', " at timepoint ", t, ": ", e$message)
    })
  }
}
object_bf2[[paste0("object_BF")]] <- b_factors
object_bf2[[paste0("object_timepoints")]] <- 1:n_timepoints 

### supra
supra_bf2 <- list()
df_valid <- as.data.frame(valid_x[['supraordinate']])
df_invalid <- as.data.frame(invalid_y[['supraordinate']])
b_factors <- rep(NA_real_, n_timepoints)
for (t in 1:n_timepoints) {
  timepoint_value_valid <- na.omit(as.numeric(df_valid[t, ]))
  timepoint_value_invalid <- na.omit(as.numeric(df_invalid[t, ]))

  if (length(timepoint_value_valid) > 1) {
    tryCatch({
      
      results <- ttestBF(
        x = timepoint_value_valid,
        y = timepoint_value_invalid,
        nullInterval = c(-0.5, 0.5),
        paired = TRUE,
        rscale = "medium",
        complement = TRUE
      )
      print(results)
      b_factors[t] <- extractBF(results)[2, "bf"]  ## 2 is the complement
      
    }, error = function(e) {
      message("Error calculating BF for ", 'supraordinate', " at timepoint ", t, ": ", e$message)
    })
  }
}
supra_bf2[[paste0("supraordinate_BF")]] <- b_factors
supra_bf2[[paste0("supraordinate_timepoints")]] <- 1:n_timepoints


output <- file.path(datapath, 'derivatives/results_main/stats/bf_differences_fullcauchy2.csv')
bayes_factors <- data.frame(
  object_BF = object_bf2[["object_BF"]],
  supraordinate_BF = supra_bf2[["supraordinate_BF"]],
  row.names = paste0("t", 1:length(object_bf[["object_BF"]]))
)
bayes_factors$time <- time
write.csv(bayes_factors, output, row.names = FALSE)






# BFs against chance
chance_list <- list()
levels <- c('supraordinate', 'object')
validity <- c('valid', 'invalid')
position <- c('front', 'behind')

for (j in 0:40) {
  subjectnr <- sprintf('%02d', j)
  for (lev in levels) {
    for (val in validity) {
      in_key <- paste0("X", subjectnr, "_behind_", val, "_", lev)
      
      chance_key <- paste(val, lev, "chance", sep = "_")

      if ("supraordinate" %in% lev) {
        chance_level <- 0.5
      } else {
        chance_level <- 1/30
      }
      
      
      if (!chance_key %in% names(chance_list)) {
        chance_list[[chance_key]] <- data.frame(row.names = times)
      }
      if (in_key %in% colnames(condition_list[[subjectnr]])) {
        chance_result <- condition_list[[subjectnr]][[in_key]] - chance_level
        
        chance_list[[chance_key]][[subjectnr]] <- chance_result
      }
    }
  }
}

Chance <- as.data.frame(chance_list)
output <- file.path(datapath, 'derivatives/results_main/stats/against_chance.csv')
write.csv(Chance, output, row.names = FALSE)



dict_bf<- list()
for (condition_code in names(chance_list)) {
  df_condition <- chance_list[[condition_code]]
  
  b_factors <- numeric(n_timepoints)
  
  for (t in 1:n_timepoints) {
    time_point_data <- as.numeric(df_condition[t, ])
    time_point_data <- time_point_data[!is.na(time_point_data)]
    
    if (length(time_point_data) > 1) {
      results <- ttestBF(x = time_point_data, mu = 0, nullInterval = c(0.5,Inf), rscale = "medium")
      
      print(results)  # Debug: print the `results` object
      
      b_factors[t] <- results
      
    }
  }
  dict_bf[[paste0(condition_code, "_chance_BF")]] <- b_factors
}


output <- file.path(datapath, 'derivatives/results_main/stats/bf_chance.csv')
bayes_factors <- as.data.frame(dict_bf)
bayes_factors$time <- time
write.csv(bayes_factors, output, row.names = FALSE)






































##### PLOTTING BFS NOT WORKING #####
# Function to create decoding plot with Bayes Factors
plot_decoding_with_bayes <- function(means, bayes_factors, condition_code, desc, chance_level) {
  
  # Prepare data for plotting
  time <- means$time
  
  # Create accuracy plot for "behind" condition
  behind_valid <- means[paste0("behind_", "valid")]
  behind_invalid <- means[paste0("behind_", "invalid")]
  
  plot_behind <- ggplot() +
    geom_line(aes(x = time, y = behind_valid), color = 'blue', linewidth = 1, linetype = "solid") +
    geom_line(aes(x = time, y = behind_invalid), color = 'red', linewidth = 1, linetype = "dashed") +
    geom_hline(yintercept = chance_level, linetype = "dotted") +
    labs(title = paste(desc, "- behind"), x = "Time (s)", y = "Accuracy") +
    theme_minimal()
  
  # Create accuracy plot for "front" condition
  front_valid <- means[paste0("front_", "valid")]
  front_invalid <- means[paste0("front_", "invalid")]
  
  plot_front <- ggplot() +
    geom_line(aes(x = time, y = front_valid), color = 'blue', linewidth = 1, linetype = "solid") +
    geom_line(aes(x = time, y = front_invalid), color = 'red', linewidth = 1, linetype = "dashed") +
    geom_hline(yintercept = chance_level, linetype = "dotted") +
    labs(title = paste(desc, "- front"), x = "Time (s)", y = "Accuracy") +
    theme_minimal()
  
  # Plot Bayes Factors for the "behind" condition
  if (!is.null(bayes_factors[[paste0("behind_", condition_code, "_diff_BF")]])) {
    bayes_data_behind <- data.frame(time = time, bf = bayes_factors[[paste0("behind_", condition_code, "_diff_BF")]])
    print(bayes_data_behind)
    plot_bayes_behind <- ggplot(bayes_data_behind, aes(x = time, y = bf)) +
      geom_line(color = 'purple', linewidth = 1) +
      scale_y_log10() +
      labs(title = paste(desc, "- Bayes Factor (behind)"), x = "Time (s)", y = "Bayes Factor (log)") +
      theme_minimal()
    
  } else {
    plot_bayes_behind <- ggplot() + labs(title = "No Bayes Factor data for behind")
  }
  
  # Plot Bayes Factors for the "front" condition
  if (!is.null(bayes_factors[[paste0("front_", condition_code, "_diff_BF")]])) {
    bayes_data_front <- data.frame(time = time, bf = bayes_factors[[paste0("front_", condition_code, "_diff_BF")]])

    plot_bayes_front <- ggplot(bayes_data_front, aes(x = time, y = bf)) +
      geom_line(color = 'purple', linewidth = 1) +
      #scale_y_log10() +
      labs(title = paste(desc, "- Bayes Factor (front)"), x = "Time (s)", y = "Bayes Factor (log)") +
      theme_minimal()
  } else {
    plot_bayes_front <- ggplot() + labs(title = "No Bayes Factor data for front")
  }
  
  # Combine plots using gridExtra
  print("before grid arrange")
  grid.arrange(plot_behind, plot_front, plot_bayes_behind, plot_bayes_front, ncol = 2)
}

# Example usage (assuming 'means_supra' and 'bayes_factors' are pre-loaded data frames or lists)

plot_decoding_with_bayes(means_supra_df, bayes_factors, 'supraordinate', 'Supraordinate Decoding', 1/2)
plot_decoding_with_bayes(means_cat_df, bayes_factors, 'category', 'Category Decoding', 1/10)
plot_decoding_with_bayes(means_obj_df, bayes_factors, 'object', 'Object Decoding', 1/30)
plot_decoding_with_bayes(means_img_df, bayes_factors, 'image', 'Image Decoding', 1/90)


##### BFs with the whole decoding average


dict_bf <- list()

for (diff_key in names(diff_list)) {
  diff_data <- diff_list[[diff_key]]
  
  # Bayes Factors for each timepoint
  b_factors <- numeric(length(diff_data))
  
  for (t in 1:length(diff_data)) {
   
    
    # Bayes Factor analysis 
      results <- ttestBF(x = time_point_data, mu = 0, rscale = "medium")
      
      # Extract the Bayes Factor value from the results
      b_factors[t] <- exp(results@bayesFactor$bf)
     
  }
  
  # Store Bayes Factors in the dictionary
  dict_bf[[paste0(diff_key, "_BF")]] <- b_factors
}


# Save the Bayes Factors for later
output_bf <- file.path(datapath, 'derivatives/stats/bf_differences.csv')
bayes_factors <- as.data.frame(dict_bf)
bayes_factors$time <- 1:length(diff_data)  # Assuming time points are sequential integers
write.csv(bayes_factors, output_bf, row.names = FALSE)
