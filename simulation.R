install.packages("DRDID")
library(DRDID)
data("sim_rc")
covX = as.matrix(sim_rc[,5:8])
reg_did_rc(y = sim_rc$y, post = sim_rc$post, D = sim_rc$d,covariates= covX)
twfe_did_rc(y = sim_rc$y, post = sim_rc$post, D = sim_rc$d,covariates= covX)
ipw_did_rc(y = sim_rc$y, post = sim_rc$post, D = sim_rc$d,covariates= covX)
std_ipw_did_rc(y = sim_rc$y, post = sim_rc$post, D = sim_rc$d,covariates= covX)
drdid_rc1(y = sim_rc$y, post = sim_rc$post, D = sim_rc$d,
          covariates= covX)
drdid_imp_rc1(y = sim_rc$y, post = sim_rc$post, D = sim_rc$d,covariates= covX)
drdid_rc2(y = sim_rc$y, post = sim_rc$post, D = sim_rc$d,
          covariates= covX)
drdid_imp_rc2(y = sim_rc$y, post = sim_rc$post, D = sim_rc$d,covariates= covX)