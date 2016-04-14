# test_words_counter

Задача - сделать консольное приложение, вычисляющее частоту встречаемости слов во
входящем потоке, а также исключить слова из референсного файла. Также поставлено ограничение
"регулируемое количество используемой памяти(минимальное 2Мб)" и возможность многопоточной
обработки.

#### Примечания
Задача стояла изначально очень простая, но мне было очень интересно посмотреть, как с ней
справятся различные варианты реализации и технологии с которыми я привык работать. Также не
совсем понятно условие ограничения на память, по скольку только интерпретатор Python
занимает в памяти около 20Мб, а само выделение памяти в питоне особо не контролируется, так
как ее освобождает сборщик мусора, а те же словари выделяют ее весьма странным образом.
Также внешние зависимости тоже могут быть весьма "прожорливы", когда речь идет о размере
памяти в 2Мб.
В итоге я трактовал это условие как необходимость минимизировать явное выделение памяти в
непосредственной логике приложения, реализовав поточную логику через генераторы и итераторы.

## Реализация
Приложение разбито на четыре логических слоя - Worker, Splitter, Source, Aggregator, каждое
из которых реализовано в нескольких вариантах так, что бы их можно было комбинировать и
посмотреть производительность каждого решения.

Источники (получение изначального потока данных):
1. StringSource: Источником является строка Python (для тестов)
2. FileSource: Получение данных из файла
3. HTTPSource: Получение данных по заданному URL. HTTP сервера должен поддерживать заголовок
Range

Splitter (отвечает за разделение строки на слова):
1. SimpleSplitter: Делит строку на слова пробегая по ней и анализируя каждый символ
2. RegexpSplitter: Анализирует регулярным выражением

Агрегаторы (собирает информацию с воркеров и формирует результат):
1. DictAggregator: Агрегация словарями Python. Исплользует примитивы multiprocessing и
вспомогательный поток для синхронизации между воркерами.
2. RedisAggregator: Агрегация через sorted set в Redis. Синхронизация между потоками
реализована за счет возможностей самого Redis.

Воркеры(распаралеливание):
1. SimpleWorker: Последовательная обработка
2. ThreadWorker: Обработка потоками Python, модуль threading
3. ProcessWorker: Обработка процессами, модуль multiprocessing
4. CeleryWorker: Обработка задачами Celery. По техническим причинам, естествнно в качестве
агрегатора может выступать только Redis(он же брокер), а если запуск воркера происходит на
другой машине, то в качестве Source сделан HTTP source. Хотя конечно можно и подмонтировать
один и тот же файл на несколько машин. Также игнорируется настройка concurrency приложения, а
используется параметр запуска самого воркера.

Таким образом на основе досточно простого примера можно посмотреть как различные технологии
справляются с этой задачей, меняя структуру от простого однопоточного приложения в
многопоточное, вплоть до вычислительного кластера (HTTPSource + Redis + Celery).

При старте источник делится на несколько равных частей между воркерами, каждый из которых
читает свою часть небольшими буферами, анализируя его через итератор слов, сливая данные
пачками в агрегатор. Отдельно анализируются слова на стыке между буферами чтения в воркере и
между пачками, выданными воркерам на уровне агрегатора.

По умолчанию приложение работает без внешних зависимостей, используя только стандартную
библиотеку Python.

Настройка используемой памяти осуществляется следующим образом:
1. read_buffer_size - размер буфера чтения. Строками такого размера(в байтах) воркер будет
читать файл-источник
2. agg_size - размер словаря(в количестве ключей), который будет собирать воркер. Как только
количество ключей будет достигнуто, воркер отправит данные в основной процесс(или редис)
3. concurrency - количество потоков. Линейно увеличивает память используемую предыдущими
двумя параметрами.

Все покрыто тестами, для того что бы они норально прошли, локально должен работать Redis и
запущен воркер Сеlery:
```
sudo pip install -r requirements.txt
sudo apt-get install redis-server
python -m celery -A  words_counter.workers.celery_worker worker --concurrency=6 --loglevel=info
```
Само приложение настраивается через файл settings.py и через командную строку (параметры
командной строки имеют приоритет):
```
python counter_app.py -i <input_file> -r <reference_file> -c <concurrency> -b <read_buffer_size> -a <aggregation_size>
```

# Выводы
Здесь и далее, скорость исполнения измерена непосредственно в коде через time.time()
(непосредственно сама обработка, без вывода данных), а объем памяти померян через
/usr/bin/time
### Объем занимаемой памяти
Оказалось, что зависимости очень сильно влияют на размер приложения. Так, если просто
запущенный питон (без приложения) занимает 24Mb. Само приложение с кодом(но без исполнения и
внешних зависимостей) только на 16Кб больше. Но если импортировать Redis, то это уже 36Мб, а
с Celery уже 60Мб, это не считая того, что нужен еще сам redis-server и воркер celery, что
оказывается весьма прожорливо.

Размер буфера чтения влияет на память линейно(помножено на количество потоков), но совершенно
незначительно. А вот объем словаря на воркере очень важен.

Размер занимаемой памяти словарем от количества элементов (замеряно через sys.getsizeof):
1. 79 элементов 3 367 байт
2. 607 элементов 31 049 байт
3. 3612 элементов 197 439 байт
4. 8228 элементов 469 551 байт
Хотя в целом размер, вероятно, зависит также от средней длины слова в анализируемом тексте.

Замер общей памяти проводился, но результаты не однозначны. На больших объемах текста
значительный объем памяти занимает итоговый словарь значений. Так, при анализе больших
текстов максимальный размер приложения в зависимости от размера словаря на воркере составил:

1. 100:   71 408k
2. 1000:  72 432k
3. 5000:  75 248k
4. 10000: 75 824k

Сложно сказать, какой объем из этого составляет неубранный мусор и накладные расходы
multiprocessing.

### Производительность

Все замеры производились тремя запусками подряд и замерялись в секундах с точностью до сотых
и округлением до ближайшего целого. В качестве входного файла была выбрана книга
"Война и мир" первый и второй том(1 473 547 байт), а в качестве референсного файла третий
и четверный том (1 519 063 байт), в поставку приложения файлы не входят.

Агрегация словарями, мультипроцессинг, буфер чтения 5КБ, 6 потоков, разбивка по размеру словаря:
1. 100:     2.95 2.24 2.71
2. 1000:    0.67 0.76 0.87
3. 5000:    0.74 0.58 0.62
4. 10000:   0.63 0.63 0.59

Как видно, маленький размер словая очень плохо сказывается, но начиная с 1000 элементов почти
не влияет на производительность.

Далее, все тестировалось агрегацией редисом.

Разные воркеры, обычная разбивка строк, 5Кб буфер чтения, размер словая 100, буфер чтения 5Кб:
1. Threads 47.88 47.98 49.58
2. Process 3.94 3.67 3.74
3. Celery 4.19 4.15 5.62

Что ожидаемо, потоки работают очень медленно(из-за GIL). Но несколько не ожиданна заметная
разница в производительности между процессами и Celery. Что для меня несколько неожданно,
так это огромная разница в производительности по сравнению со словарями. Я ожидал, что при
больших объемах словарей Redis будет более эффективным решением.

Тоже, но для Regexp разбивки строк:
1. Threads 48.83 49.23 48.60
2. Process 3.40 3.37 3.67
3. Celery 4.63 4.13 4.14

В целом, скорость почти такая же. Довольно странно(и не очень понятно), но на потоках
регулярные выражения работают несколько медленнее, а на процессах и селери немного быстрее.

Производительность и занимаемая память для регулярных выражений в зависимости от количества потоков,
multiprocessing, regexp, словарь 100, буфер 5Кб на машине с 4 физическими ядрами:
1. 6:  3.40 3.37 3.67 -   38256k max resident
2. 8:  3.29 3.27 3.20 - 60160k max resident
3. 12: 3.21 3.27 3.20 - 60160k max resident
4. 14: 3.36 3.22 3.29

Что ожидаемо, производтельность не особо меняется, по скольку в обработке практически нет
ожидания внешних процессов(редис работает очень быстро, а на локальной машине нет сетевых
задержек)

Влияние буфера чтения, multiprocessing, regexp, 8 потоков, размер словаря 100:
1. 1Kb:   3.31 3.23 3.20 - 60160k max resident
2. 5Kb :  3.29 3.27 3.20 - 60128k max resident
3. 10Kb:  3.28 3.19 3.16 - 60144k max resident
4. 20Kb:  3.22 3.37 3.24 - 60160k max resident

Что ожидаемо, буфер практически не влияет на производительность и память.

Влияние размера словаря на воркере, multiprocessing, regexp,8 потоков, буфер 10кб:

1. 100:   3.28 3.19 3.16  -    60144k max resident
2. 1000:  2.45 2.34 2.38  -    61936k max resident
3. 10000: 1.81 1.84 1.75  -    73296k max resident
4. 100000:1.61 1.67 1.67  -    79184k max resident

