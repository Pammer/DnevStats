a = Analysis(['main.py'],
             hookspath=['.\\hooks\\'],
             runtime_hooks=None,
             datas=[
                    ('C:\\Users\\rtkli91\\AppData\\Local\\Programs\\Python\\Python37-32\\Lib\\site-packages\\scrapy\\VERSION', '.\\scrapy\\'), 
                    ('C:\\Users\\rtkli91\\AppData\\Local\\Programs\\Python\\Python37-32\\Lib\\site-packages\\scrapy\\mime.types', '.\\scrapy\\'),
                    ('api-ms-win-crt-runtime-l1-1-0.dll', '.')
                   ]
             )
pyz = PYZ(a.pure)

options = [('u', None, 'OPTION'), ('u', None, 'OPTION'), ('u', None, 'OPTION')]

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          options,
          name='GetSomeStatisticFromDnev',
          debug=False,
          strip=None,
          upx=False,
          console=True,
          windowed=False)
