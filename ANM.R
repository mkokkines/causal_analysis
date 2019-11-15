test <- function(x, y, reg_model = train_GAMboost, ind_test = indtestHsic, cut_off = 10, verbose = FALSE) {
    xToY <- reg_model(x, y)
    yToX <- reg_model(y, x)
    xToY.P <- ind_test(xToY$residuals, x)$p.value
    yToX.P <- ind_test(yToX$residuals, y)$p.value
    if (xToY.P > 10 * yToX.P) {
        result <- TRUE
    } else if (xToY.P * 10 < yToX.P) {
        result <- FALSE
    } else {
        result <- NA
    }

    if (verbose) {
        message("P value for forward is ", xToY.P, ", P value for backword is ", yToX.P, " result is ", ifelse(is.na(result), "Inconclusive", result))
    }
    
    c(result, xToY.P, yToX.P)
}

shift <- function(x, col_names, lags = 1) {
    name <- "y"
    x[, name] <- NA
    x[1 : (nrow(x) - lags), name] <- x[(lags + 1) : nrow(x), col_names]
    x = x[1 : (nrow(x) - lags), ]
}

file_test <- function(file, col_names, reg_model = train_GAMboost, ind_test = indtestHsic, cut_off = 10, lags = 1, collection = 1 : 12, verbose = FALSE) {
    data <- read.csv(file, skip = 11)
    data[data == " M"] <- NA
    data$x <- as.numeric(data[, col_names])
    data <- data[, c("Date", "x")]
    data <- na.omit(shift(data, "x", lags))
    
    collection_result <- matrix(0, length(collection), 3)
    for (i in collection) {
        curr <- data[month(data$Date) %in% i, ]
        result <- test(curr$x, curr$y, verbose = verbose)
        collection_result[i, ] = c(ifelse(is.na(result[1]), -1, as.numeric(result)[1]), result[2:3])
    }

    collection_result
}

dir = "/Users/markcao/Documents/Course/2019Fall/Research/top100"
setwd(dir)
source("../fitting.R")
source("../indtestHsic.R")
files = list.files(dir)
## sink("../result.log", type = c("output", "message"))

count <- 0
result <- data.frame(FileName = character(),
                     TestParameter = character(),
                     TestLag = integer(),
                     RegressionModel = character(),
                     Collection = factor(),
                     ForwardPValue = double(),
                     BackwardPValue = double(),
                     Result = factor())

parameters <- c("Min.Temperature",
                "Max.Temperature")

lags = 1

models <- c("train_linear",
            "train_gp",
            "train_gam",
            "train_GAMboost",
            "train_penGAM",
            "train_lasso")

for (file in files) {
    message("Start ", count, " testing file: ", file)
    message("/n")
    count <- count + 1
    for (test_para in parameters) {
        for (lag in lags) {
            message("Test parameter: ", test_para)
            for (reg_model in models) {
                message("Using Model: ", reg_model)
                f_result <- file_test(file = file,
                                      col_names = test_para,
                                      reg_model = eval(reg_model),
                                      lags = lag)
                
                for (r in (1 : nrow(f_result))) {
                    curr_result <- factor("TRUE")
                    if (f_result[r, 1] == 0 ) {
                        curr_result <- factor("FALSE")
                    } else if (f_result[r, 1] == -1 ) {
                        curr_result <- factor("Inconclusive")
                    }
                    
                    curr <- list(FileName = file,
                                 TestParameter = test_para,
                                 TestLag = lag,
                                 RegressionModel = reg_model,
                                 Collection = r,
                                 ForwardPValue = f_result[r, 2],
                                 BackwardPValue = f_result[r, 3],
                                 Result = curr_result)

                    result <- rbind(result, curr, stringsAsFactors = FALSE)
                }
            }
        }
    }
}

write.csv(result, "../AllOutput.csv", row.names = FALSE)
