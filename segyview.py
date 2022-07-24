import segyio
import matplotlib.pyplot as plt
folder=r'.//'
# path=folder+'img.segy'
path='img.segy'
path='Seismic_data_to_be_digitized_bad_quality.segy'
path='Seismic_data_to_be_digitized_good_quality.segy'
f = segyio.open(path)
x = segyio.tools.collect(f.trace[:])


plt.figure(figsize=(16,16))

plt.imshow(x.T, cmap=plt.cm.BuPu_r)
plt.show()