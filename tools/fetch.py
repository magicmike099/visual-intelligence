import pyarrow.dataset as ds, pyarrow.fs as fs, pyarrow.compute as pc, sys, time
s3=fs.S3FileSystem(anonymous=True, region='us-west-2')
theme, typ, out = sys.argv[1], sys.argv[2], sys.argv[3]
X0,Y0,X1,Y1=2.22,48.81,2.475,48.905
d=ds.dataset(f'overturemaps-us-west-2/release/2026-09-23.1/theme={theme}/type={typ}/',filesystem=s3,format='parquet')
f=(pc.field('bbox','xmin')>X0)&(pc.field('bbox','xmax')<X1)&(pc.field('bbox','ymin')>Y0)&(pc.field('bbox','ymax')<Y1)
cols=sys.argv[4].split(',')
t=time.time()
tbl=d.to_table(filter=f,columns=cols)
import pyarrow.parquet as pq; pq.write_table(tbl,out)
print(tbl.num_rows, time.time()-t)
