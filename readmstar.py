import numpy as np
import cPickle as pickle
import sys
import os

def readMSTARFile(filename):
# raw_input('Enter the mstar file to read: ')

	#print filename

	f = open(filename, 'rb')

	a = ''

	phoenix_header = []

	while 'PhoenixHeaderVer' not in a:
		a = f.readline()

	a = f.readline()

	while 'EndofPhoenixHeader' not in a:
		phoenix_header.append(a)
		a = f.readline()

	data = np.fromfile(f, dtype='>f4')

	# print data.shape

	# magdata = data[:128*128]
	# phasedata = data[128*128:]

	# if you want to print an image
	# imdata = magdata*255

	# imdata = imdata.astype('uint8')

	targetSerNum = '-'

	for line in phoenix_header:
		#print line
		if 'TargetType' in line:
			targetType = line.strip().split('=')[1].strip()
		elif 'TargetSerNum' in line:
			targetSerNum = line.strip().split('=')[1].strip()

	label = targetType# + '_' + targetSerNum

	return data.astype('float32'), label, targetSerNum

def readMSTARDir(dirname):
	data = np.zeros([32768,0],dtype = 'float32')
	labels = []
	serNums = []
	files = os.listdir(dirname)

	for f in files:
		fullpath = os.path.join(dirname,f)
		if os.path.isdir(fullpath):
			d,l,sn = readMSTARDir(fullpath)
			data = np.concatenate((data,d),axis=1)
			labels = labels + l
			serNums = serNums + sn
		else:
			d,l,sn = readMSTARFile(os.path.join(dirname,f))
			data = np.concatenate((data,d.reshape(-1,1)),axis=1)
			labels = labels + [l]
			serNums = serNums + [sn]

	return data, labels, serNums

if len(sys.argv) < 3:
	sys.exit()

filename = sys.argv[1]
outputfile = sys.argv[2]

data, labels, serNums = readMSTARDir(os.path.join(filename,'TRAIN'))

mstar_dic_train = dict()

mstar_dic_train['data'] = data
mstar_dic_train['labels'] = labels
mstar_dic_train['serial numbers'] = serNums

data, labels, serNums = readMSTARDir(os.path.join(filename,'TEST'))

mstar_dic_test = dict()

mstar_dic_test['data'] = data
mstar_dic_test['labels'] = labels
mstar_dic_test['serial numbers'] = serNums

labels = list(set(labels))

label_dict = dict()

for i in range(len(labels)):
	label_dict[labels[i]] = i

for i in range(len(mstar_dic_train['labels'])):
	mstar_dic_train['labels'][i] = label_dict[mstar_dic_train['labels'][i]]

for i in range(len(mstar_dic_test['labels'])):
	mstar_dic_test['labels'][i] = label_dict[mstar_dic_test['labels'][i]]


f = open(os.path.join(outputfile,'data_batch_1'),'wb')
pickle.dump(mstar_dic_train,f)

f.close()

f = open(os.path.join(outputfile,'test_batch'),'wb')
pickle.dump(mstar_dic_test,f)

f.close()

meta_dic = dict()

meta_dic['num_cases_per_batch'] = len(mstar_dic_train['labels'])
meta_dic['label_names'] = labels

f = open(os.path.join(outputfile,'batches.meta'),'wb')
pickle.dump(meta_dic,f)

f.close()
# print phoenix_header
