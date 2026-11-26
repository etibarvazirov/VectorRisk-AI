import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import io
st.set_page_config(page_title='VectorRisk AI',page_icon='🛰️',layout='wide')
st.markdown('''<style>
.stApp {background:#f0f5f7;color:#142d3b;} [data-testid="stSidebar"] {background:#e0ebef;} [data-testid="stSidebar"] * {color:#142d3b !important;} .stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label,[data-testid="stMetricValue"],[data-testid="stMetricLabel"] {color:#142d3b !important;} .hero {background:#123b50;color:#fff;padding:28px;border-radius:16px;border-left:8px solid #37b9a5;} .hero h1,.hero p {color:#fff !important;} [data-baseweb="select"] {color:#142d3b;} </style>''',unsafe_allow_html=True)
lang=st.sidebar.radio('Language / Dil / Язык',['AZ','EN','RU'],horizontal=True)
def T(a,e,r): return {'AZ':a,'EN':e,'RU':r}[lang]
st.markdown('<div class="hero"><h1>VectorRisk AI</h1><p>Satellite intelligence × epidemiology | Research observatory</p></div>',unsafe_allow_html=True)
nav=st.sidebar.radio(T('Bölmələr','Sections','Разделы'),[T('Layihə haqqında','About','О проекте'),T('Peyk atlası','Satellite atlas','Спутниковый атлас'),T('Proqnozlar','Forecasts','Прогнозы'),T('Elmi nəticələr','Research findings','Результаты'),T('Öz peyk faylın','Custom imagery','Свои снимки')])
D=Path(__file__).parent/'data'
@st.cache_data
def read(name): return pd.read_csv(D/name)
if nav==T('Layihə haqqında','About','О проекте'):
 st.header(T('Dengue riskini kosmosdan öyrənirik','Studying dengue risk from space','Изучаем риск денге из космоса'))
 st.write(T('Dengue ağcaqanadlarla yayılan xəstəlikdir. Temperatur, rütubət, yağıntı və ətraf mühit onun yayılması ilə əlaqəli ola bilər. Layihəmiz peyk məlumatlarının əvvəlki xəstəlik sayı və hava məlumatlarına əlavə proqnoz dəyəri verib-vermədiyini yoxlayır.','Dengue is a mosquito-borne disease. Temperature, humidity, rainfall and environmental conditions may relate to transmission. We test whether satellite data add forecasting value beyond case history and weather.','Денге передаётся комарами. Температура, влажность, осадки и среда могут быть связаны с распространением. Мы проверяем, улучшают ли спутниковые данные прогнозы на основе истории случаев и погоды.'))
 for col,(v,l) in zip(st.columns(4),[('5',T('Şəhər','Cities','Городов')),('191',T('Emal edilmiş görüntü','Processed scenes','Снимков')),('161',T('QA keçən görüntü','QA-passed scenes','Прошли контроль')),('2 / 4',T('Həftəlik üfüq','Weeks ahead','Недель вперёд'))]): col.metric(l,v)
 st.subheader(T('Necə işləyir?','How it works','Как это работает'))
 st.write(T('Sentinel-2 spektral kanalları → keyfiyyət maskası → NDVI (bitki), NDWI (su), NDBI (tikili proxy) → epidemioloji və meteoroloji xüsusiyyətlərlə birləşdirmə → 2 və 4 həftəlik proqnoz → statistik müqayisə.','Sentinel-2 bands → quality mask → NDVI (vegetation), NDWI (water), NDBI (built-up proxy) → merge with epidemiology and weather → 2/4-week forecasts → statistical comparison.','Каналы Sentinel-2 → маска качества → NDVI (растительность), NDWI (вода), NDBI (застройка, прокси) → объединение с эпидемиологией и погодой → прогноз на 2/4 недели → статистическое сравнение.'))
 st.info(T('M0: son məlum xəstəlik sayı; M1: epidemiologiya; M2: M1 + hava; M3: M2 + peyk indeksləri; M4: M3 + məkan-zaman xüsusiyyətləri.','M0: last known case count; M1: epidemiology; M2: M1 + weather; M3: M2 + satellite indices; M4: M3 + spatial-temporal features.','M0: последнее известное число случаев; M1: эпидемиология; M2: M1 + погода; M3: M2 + спутниковые индексы; M4: M3 + пространственно-временные признаки.'))
 st.warning(T('Tədqiqat prototipi: 5 şəhər, 3×3 km mərkəz sahələri, fərz edilən məlumat gecikmələri, təkrar yoxlanılmış 2025. Real vaxt xəbərdarlığı və səbəb-nəticə iddiası yoxdur.','Research prototype: five cities, 3×3 km central patches, assumed data delays, repeatedly inspected 2025. No real-time alert or causal claim.','Исследовательский прототип: пять городов, участки 3×3 км, предполагаемые задержки данных, повторно изученный 2025 год. Не система реального времени; причинность не доказана.'))
elif nav==T('Öz peyk faylın','Custom imagery','Свои снимки'):
 st.header(T('Kalibrasiya edilmiş GeoTIFF analizi','Calibrated GeoTIFF analysis','Анализ калиброванных GeoTIFF'))
 st.write(T('Eyni grid və CRS-də, buludları maskalanmış, 0–1 reflectance vahidində 4 təkkanallı GeoTIFF yüklə. Adi foto uyğun deyil.','Upload four aligned single-band GeoTIFFs in 0–1 reflectance units, with clouds masked. Ordinary photos are unsuitable.','Загрузите четыре совмещённых одноканальных GeoTIFF с отражательной способностью 0–1 и маской облаков. Обычные фото не подходят.'))
 files=[st.file_uploader(b,type=['tif','tiff'],key=b) for b in ['Red (B04)','Green (B03)','NIR (B08)','SWIR (B11)']]
 if st.button(T('İndeksləri hesabla','Calculate indices','Рассчитать индексы'),disabled=not all(files)):
  try:
   from rasterio.io import MemoryFile
   arr=[]; grids=[]
   for f in files:
    with MemoryFile(f.getvalue()) as mem,mem.open() as ds:
     if ds.count!=1 or ds.crs is None or ds.width*ds.height>4000000: raise ValueError('Single band, CRS and ≤4M pixels required')
     grids.append((ds.shape,ds.transform,ds.crs)); a=ds.read(1,masked=True).astype('float32').filled(np.nan)
     if not np.isfinite(a).any() or np.nanmin(a)<0 or np.nanmax(a)>1: raise ValueError('Expected calibrated reflectance 0–1')
     arr.append(a)
   if any(g!=grids[0] for g in grids): raise ValueError('Grid/CRS mismatch')
   red,green,nir,swir=arr
   for col,(name,a,b) in zip(st.columns(3),[('NDVI',nir,red),('NDWI',green,nir),('NDBI',swir,nir)]):
    z=np.divide(a-b,a+b,out=np.full_like(a,np.nan),where=(a+b)>.01); fig,ax=plt.subplots(); im=ax.imshow(z,vmin=-1,vmax=1,cmap='BrBG'); ax.set_title(name); ax.axis('off'); fig.colorbar(im,ax=ax); col.pyplot(fig); plt.close(fig)
   st.info(T('Yalnız ekoloji analizdir; xəstəlik proqnozu deyil.','Environmental analysis only; not a disease forecast.','Только анализ среды; не прогноз заболевания.'))
  except Exception as e: st.error(str(e))
else:
 try:
  if nav==T('Peyk atlası','Satellite atlas','Спутниковый атлас'):
   m=read('scenes.csv'); st.map(m[['lat','lon']].drop_duplicates()); city=st.selectbox(T('Şəhər','City','Город'),sorted(m.city.unique())); q=m[m.city==city]; month=st.selectbox(T('Ay','Month','Месяц'),sorted(q.month.unique(),reverse=True)); r=q[q.month==month].iloc[0]; st.caption(str(r.scene_id)+' | '+str(r.acquisition)); z=np.load(D/'scenes'/r.file,allow_pickle=False)
   for col,k in zip(st.columns(3),['NDVI','NDWI','NDBI']):
    fig,ax=plt.subplots(); im=ax.imshow(z[k],vmin=-1,vmax=1,cmap='BrBG'); ax.set_title(k); ax.axis('off'); fig.colorbar(im,ax=ax); col.pyplot(fig); plt.close(fig)
   st.caption(T('3×3 km şəhər mərkəzi; bütün şəhər deyil.','3×3 km city-center patch, not the entire city.','Участок центра 3×3 км, не весь город.'))
  else:
   h=st.sidebar.selectbox(T('Üfüq (həftə)','Horizon (weeks)','Горизонт (недели)'),[2,4]); delay=st.sidebar.selectbox(T('Gecikmə (həftə)','Delay (weeks)','Задержка (недели)'),[1,2]); protocol=st.sidebar.selectbox(T('Protokol','Protocol','Протокол'),['temporal','geographic'],format_func=lambda x:T('Zaman','Temporal','Временной') if x=='temporal' else T('Coğrafi','Geographic','Географический'))
   def filt(d): return d[(d.horizon==h)&(d.delay==delay)&(d.protocol==protocol)]
   if nav==T('Proqnozlar','Forecasts','Прогнозы'):
    p=filt(read('predictions.csv')); city=st.selectbox(T('Şəhər','City','Город'),sorted(p.municipio.unique())); p=p[p.municipio==city]; p['target_week_end']=pd.to_datetime(p.origin_date)+pd.to_timedelta(7*h,unit='D'); models=st.multiselect(T('Modellər','Models','Модели'),['M0','M1','M2','M3','M4'],default=['M0','M2','M3']); w=p.pivot(index='target_week_end',columns='model',values='prediction'); w[T('Faktiki','Actual','Факт')]=p.groupby('target_week_end').actual.first(); st.line_chart(w[models+[T('Faktiki','Actual','Факт')]]); st.caption(T('2025 retrospektiv proqnozları; tarix hədəf həftəsinin sonudur.','2025 retrospective forecasts; date is target week end.','Ретроспективные прогнозы 2025; дата — конец целевой недели.')); st.dataframe(p[['target_week_end','model','actual','prediction','anchor']],hide_index=True)
    hist=read('history.csv'); hist=hist[hist.municipio==city].copy(); hist['data_iniSE']=pd.to_datetime(hist.data_iniSE); st.subheader(T('Tarixi xəstəlik sayı','Historical case counts','История случаев')); st.line_chart(hist.set_index('data_iniSE').casos)
   else:
    m=filt(read('metrics.csv')).set_index('model'); st.bar_chart(m[['MAE']]); st.bar_chart(m[['macro_WAPE']]*100); st.caption(T('Macro-WAPE: şəhərlər üzrə bərabər çəkili nisbi xəta (%); aşağı daha yaxşıdır.','Macro-WAPE: equal-city relative error (%); lower is better.','Macro-WAPE: относительная ошибка с равными весами городов (%); ниже лучше.')); b=filt(read('bootstrap.csv')); b=b[(b.block_weeks==8)&(b.metric=='macro_WAPE')]; st.dataframe(b[['candidate','reference','relative_pct','improvement','ci_low','ci_high']],hide_index=True); st.caption(T('İntervallar nisbət vahidindədir (0.01 = 1 faiz bəndi); çoxsaylı müqayisələrə korrektə yoxdur.','Intervals are fractions (0.01 = 1 percentage point); no multiplicity adjustment.','Интервалы в долях (0.01 = 1 процентный пункт); без поправки на множественность.')); st.info(T('M3 M2-ni 8/8 ssenaridə Macro-WAPE üzrə üstələyib; M0 isə əsas metrikdə daha güclüdür. M4 üstünlüyü təsdiqlənməyib.','M3 beats M2 on Macro-WAPE in 8/8 scenarios; M0 remains stronger on the primary metric. M4 superiority is not established.','M3 лучше M2 по Macro-WAPE в 8/8 сценариях; M0 сильнее по основной метрике. Превосходство M4 не установлено.'))
 except (FileNotFoundError,KeyError,ValueError) as e: st.error(T('Demo məlumatları hazır deyil: 09 notebook-u icra et.','Demo data unavailable: run notebook 09.','Демо-данные недоступны: выполните ноутбук 09.')+' '+str(e))
