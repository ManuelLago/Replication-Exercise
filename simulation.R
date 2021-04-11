install.packages("DRDID")
library(DRDID)
data("nsw_long")
# Form the Lalonde sample with CPS comparison group
eval_lalonde_cps <- subset(nsw_long, nsw_long$treated == 0 | nsw_long$sample == 2)
# Implement OR DID with panel data
ordid(yname="re", tname = "year", idname = "id", dname = "experimental",
      xformla= ~ age+ educ+ black+ married+ nodegree+ hisp+ re74,
      data = eval_lalonde_cps, panel = TRUE)

# Form the Lalonde sample with CPS comparison group
eval_lalonde_cps <- subset(nsw, nsw$treated == 0 | nsw$sample == 2)
# Select some covariates
covX = as.matrix(cbind(eval_lalonde_cps$age, eval_lalonde_cps$educ,
                       eval_lalonde_cps$black, eval_lalonde_cps$married,
                       eval_lalonde_cps$nodegree, eval_lalonde_cps$hisp,
                       eval_lalonde_cps$re74))
# Implement TWFE DID with panel data
twfe_did_panel(y1 = eval_lalonde_cps$re78, y0 = eval_lalonde_cps$re75,
               D = eval_lalonde_cps$experimental,
               covariates = covX)

# Form the Lalonde sample with CPS comparison group
eval_lalonde_cps <- subset(nsw_long, nsw_long$treated == 0 | nsw_long$sample == 2)

# Implement IPW DID with panel data (normalized weights)
ipwdid(yname="re", tname = "year", idname = "id", dname = "experimental",
       xformla= ~ age+ educ+ black+ married+ nodegree+ hisp+ re74,
       data = eval_lalonde_cps, panel = TRUE)

# Form the Lalonde sample with CPS comparison group
eval_lalonde_cps <- subset(nsw_long, nsw_long$treated == 0 | nsw_long$sample == 2)
# -----------------------------------------------
# Implement improved DR locally efficient DID with panel data
drdid(yname="re", tname = "year", idname = "id", dname = "experimental",
      xformla= ~ age+ educ+ black+ married+ nodegree+ hisp+ re74,
      data = eval_lalonde_cps, panel = TRUE)

# Form the Lalonde sample with CPS comparison group (data in wide format)
eval_lalonde_cps <- subset(nsw, nsw$treated == 0 | nsw$sample == 2)
# Select some covariates
covX = as.matrix(cbind(eval_lalonde_cps$age, eval_lalonde_cps$educ,
                       eval_lalonde_cps$black, eval_lalonde_cps$married,
                       eval_lalonde_cps$nodegree, eval_lalonde_cps$hisp,
                       eval_lalonde_cps$re74))

# Implement traditional DR locally efficient DID with panel data
drdid_panel(y1 = eval_lalonde_cps$re78, y0 = eval_lalonde_cps$re75,
            D = eval_lalonde_cps$experimental,
            covariates = covX)