cd ~/data/fmri/Analogy/data
for s in analogy*
do
echo ${s}
fslcpgeom ${s}/analysis/reg/BOLD_template ../analysis/multivariate/searchlight/raw/${s}_svm_abmainrel_ab2cd_cvsl.nii.gz -d
done

# fslcpgeom ${s}/analysis/reg/BOLD_template ../analysis/multivariate/searchlight/raw/${s}_grayMatter_ab2cd_cvsl -d

# fslcpgeom ${s}/analysis/reg/BOLD_template ../analysis/multivariate/searchlight/vis/${s}_svm_abmainrel_abmainrel_cvsl -d

# fslcpgeom ${s}/analysis/reg/BOLD_template ../analysis/multivariate/searchlight/raw/${s}_grayMatter_abmainrel_cvsl -d
# fslchfiletype NIFTI_PAIR ${s}/analysis/reg/BOLD_template
# fslchfiletype NIFTI_PAIR ../analysis/multivariate/searchlight/raw/${s}_grayMatter_abmainrel_cvsl
# cp ${s}/analysis/reg/BOLD_template.hdr ../analysis/multivariate/searchlight/raw/${s}_grayMatter_abmainrel_cvsl.hdr

# fslchfiletype NIFTI_GZ ../analysis/multivariate/searchlight/raw/${s}_grayMatter_abmainrel_cvsl
# fslchfiletype NIFTI_GZ ${s}/analysis/reg/BOLD_template


