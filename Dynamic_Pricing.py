############################################
# DYNAMIC PRICING
############################################

###########################################
# 1.Veri Hazırlama
############################################

#Gerekli kütüphaneler import edildi.
import pandas as pd
import itertools
import statsmodels.stats.api as sms
from scipy.stats import shapiro
import scipy.stats as stats
from helpers.helpers import replace_with_thresholds,check_df,analysis_df, outlier_thresholds
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

# Veri seti okuma
df = pd.read_csv(r'C:\Users\LENOVO\PycharmProjects\DSMLBC4\HAFTA_05\pricing.csv', sep=";")
analysis_df(df)

# Shapiro testi ile normallik varsayımı test edildi.
print(" Shapiro Test Sonucu")
for category in df["category_id"].unique():
    test_statistic , pvalue = shapiro(df.loc[df["category_id"] ==  category,"price"])
    if(pvalue<0.05):
        print('\n','{0} -> '.format(category),'Test statistic = %.4f, p-Value = %.4f' % (test_statistic, pvalue),"H0 RED.")
    else:
         print('Test statistic = %.4f, p-Value = %.4f' % (test_statistic, pvalue),"H0 REDDEDİLEMEZ.")

#Shapiro Test Sonucu
#489756 ->  Test statistic = 0.1095, p-Value = 0.0000 H0 RED.
#361254 ->  Test statistic = 0.0615, p-Value = 0.0000 H0 RED.
#874521 ->  Test statistic = 0.1311, p-Value = 0.0000 H0 RED.
#326584 ->  Test statistic = 0.0568, p-Value = 0.0000 H0 RED.
#675201 ->  Test statistic = 0.1011, p-Value = 0.0000 H0 RED.
#201436 ->  Test statistic = 0.6190, p-Value = 0.0000 H0 RED.

# Aykırı değerler için alt limit ve üst limit belirlendi.
def outlier_thresholds(dataframe, variable, low_quantile=0.05, up_quantile=0.95):
    quantile_one = dataframe[variable].quantile(low_quantile)
    quantile_three = dataframe[variable].quantile(up_quantile)
    interquantile_range = quantile_three - quantile_one
    up_limit = quantile_three + 1.5 * interquantile_range
    low_limit = quantile_one - 1.5 * interquantile_range
    return low_limit, up_limit

# Price değişkeni için eşik değerleri belirlendi.
low_limit,up_limit = outlier_thresholds(df, "price")
print("Low Limit : {0}  Up Limit : {1}".format(low_limit,up_limit))

# Aykırı gözlem kontrolü.
def has_outliers(dataframe, numeric_columns):

    for col in numeric_columns:
        low_limit, up_limit = outlier_thresholds(dataframe, col)
        if dataframe[(dataframe[col] > up_limit) | (dataframe[col] < low_limit)].any(axis=None):
            number_of_outliers = dataframe[(dataframe[col] > up_limit) | (dataframe[col] < low_limit)].shape[0]
            print(col, " : ", number_of_outliers, "outliers")
has_outliers(df, ["price"])

#Çıktı = price  :  77 outliers


# Aykırı değerlerin veri setinden uzaklaştırılması.
def remove_outliers(dataframe, numeric_columns):
    for variable in numeric_columns:
        low_limit, up_limit = outlier_thresholds(dataframe, variable)
        dataframe_without_outliers = dataframe[~((dataframe[variable] < low_limit) | (dataframe[variable] > up_limit))]
    return dataframe_without_outliers

df = remove_outliers(df, ["price"])

#Gözlem sayımızı kontrol edelim
df.shape #(3371, 2)


############################
# AB Testi (Bağımsız İki Örneklem T Testi)
############################

############################
# 1. Varsayım Kontrolü
############################

# 1.1 Normallik Varsayımı
# 1.2 Varyans Homojenliği

############################
# 1.1 Normallik Varsayımı
############################

# H0: Normal dağılım varsayımı sağlanmaktadır.
# H1:..sağlanmamaktadır.


#Shapiro testi ile normallik varsayımı.

print(" Shapiro Test Sonucu")
for category in df["category_id"].unique():
    test_statistic , pvalue = shapiro(df.loc[df["category_id"] ==  category,"price"])
    if(pvalue<0.05):
        print('\n','{0} -> '.format(category),'Test statistic = %.4f, p-Value = %.4f' % (test_statistic, pvalue),"H0 RED.")
    else:
         print('Test statistic = %.4f, p-Value = %.4f' % (test_statistic, pvalue),"H0 REDDEDİLEMEZ.")

#Shapiro Test Sonucu
#489756 ->  Test statistic = 0.6328, p-Value = 0.0000 H0 RED.
#361254 ->  Test statistic = 0.4757, p-Value = 0.0000 H0 RED.
#874521 ->  Test statistic = 0.5116, p-Value = 0.0000 H0 RED.
#326584 ->  Test statistic = 0.5026, p-Value = 0.0000 H0 RED.
#675201 ->  Test statistic = 0.6382, p-Value = 0.0000 H0 RED.
#201436 ->  Test statistic = 0.6190, p-Value = 0.0000 H0 RED.

# p-value < ise 0.05'ten HO RED. Normallik varsayımı sağlanmadı bu nedenle mannwhitneyu testi (non-parametrik test) uygulayacağız.


# Kategori kombinasyonlarının oluşturulması.
cat_com = []
for x in itertools.combinations(df["category_id"].unique(),2):
    cat_com.append(x)
cat_com #pair=x pairs=cat_Com

result=[]
print("Levene Testi Sonucu")
for x in cat_com:
    test_statistic,pvalue = stats.levene(df.loc[df["category_id"] == x[0], "price"], df.loc[df["category_id"] == x[1], "price"])
    if(pvalue < 0.05):
        print('\n',"({0} - {1}) -> ".format(x[0], x[1]), 'Test statistic = %.4f, p-Value = %.4f' % (test_statistic, pvalue), "  H0 RED.")
    else:
         print('\n',"({0} - {1}) -> ".format(x[0], x[1]), 'Test statistic = %.4f, p-Value = %.4f' % (test_statistic, pvalue), "  H0 REDDEDİLEMEZ.")

result_df = pd.DataFrame()
result_df["Category 1"] = [x[0] for x in result]
result_df["Category 2"] = [x[1] for x in result]
result_df["H0"] = [x[2] for x in result]

result_df

result_df[result_df["H0"] == "H0 REDDEDİLEMEZ."]


df.groupby("category_id").agg({"price":"mean"})

# Benzerlik gösteren kategoriler seçildi.
signif_cat = [361254,874521,675201,201436]
sum = 0
for i in signif_cat:
    sum += df.loc[df["category_id"]== i,"price"].mean()
PRICE = sum/4


print("PRICE :{%.4f}"%PRICE)

# Seçilen benzer kategorilerin fiyat listesi.
prices = []
for category in signif_cat:
    for i in df.loc[df["category_id"]== category,"price"]:
        prices.append(i)



print("Esnek Fiyat Aralığı: ", sms.DescrStatsW(prices).tconfint_mean())

# ÇIKTI : Esnek Fiyat Aralığı:  (36.7109597897918, 38.17576299427283)


# Ürün Gelirlerinin Simüle Edilmesi:

# Güven aralığının min ve max değerlerinden elde edilebilecek gelirleri hesaplayalım.
# MİN değerine göre
freq = len(df[df["price"]>=37.09238177238653])
income = freq * 37.09238177238653
print("Beklenen Gelir: ", income)

# Beklenen Gelir:  37611.67511719994

# MAX değerine göre
freq = len(df[df["price"]>=38.17576299427283])
income = freq * 38.17576299427283
print("Beklenen Gelir: ",income)

# Beklenen Gelir:  35388.93229569092


# ÖZET
# Yapılan testler sonucu ürün kategorileri arasında istatistiksel bir farklılık olmadığına karar verildi.
# Tüm ürün kategorilerinde normallik varsayımı testinde H0:RED sonucunu aldık. Bu nedenle non-parametrik (bağımsız iki örneklem t testi) uygulandı.
# Benzer kategoriler seçildi ve bunlar baza alınarak güven aralıkları oluşturuldu. Beklenen fiyatlar güven aralığına göre simüle edildi.
