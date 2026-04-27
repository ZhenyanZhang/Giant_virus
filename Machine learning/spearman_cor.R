wd <- "D:/giant_virus/machine_learning"
setwd(wd)

library(tidyverse)
library(ggdendro)

# ==========================================
# 1. Data loading
# ==========================================
env_df <- read.delim("env_table.txt", stringsAsFactors = FALSE)

env_data <- env_df %>%
  column_to_rownames("sample")

# ==========================================
# 2. spearman's r calculating and clusting
# ==========================================
cor_env <- cor(env_data, method = "spearman")

dist_env <- as.dist(1 - abs(cor_env))

hc_env <- hclust(dist_env, method = "average")

# ==========================================
# 3. ploting
# ==========================================
dendro_data_env <- dendro_data(hc_env, type = "rectangle")

plot_dendro <- ggplot(segment(dendro_data_env)) +
  geom_segment(aes(x = x, y = y, xend = xend, yend = yend), size = 0.1) +
  geom_hline(yintercept = 0.4, color = "red", linetype = "dotted", size = 1) +
  scale_x_continuous(
    expand = c(0.02, 0),
    breaks = seq_along(hc_env$labels), 
    labels = hc_env$labels[hc_env$order] 
  ) +
  scale_y_continuous(expand = c(0, 0.05), breaks = seq(0, 1, by = 0.2)) +
  ylab("1 - |Spearman's rho|") +
  theme_classic() +
  theme(
    axis.title.x = element_blank(),
    axis.text.x = element_text(angle = 90, hjust = 1, vjust = 0.5, size = 10, color = "black"),
    axis.ticks.x = element_blank(),
    axis.line.x = element_blank(),
    axis.text.y = element_text(size = 10, color = "black"),
    axis.title.y = element_text(size = 11, color = "black", face = "bold"),
    plot.margin = margin(t = 10, r = 10, b = 10, l = 10) 
  )

print(plot_dendro)