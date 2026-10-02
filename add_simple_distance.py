#!/usr/bin/env python3
import sys
path = sys.argv[1]
src = open(path, encoding='utf-8').read()

# 1. Shorten the label of the flexible port-based block
old_text = "default: 'distance on port [PORT]',"
new_text = "default: 'distance [PORT]',"
if src.count(old_text) == 1:
    src = src.replace(old_text, new_text)
    print('OK: подпись блока сокращена до "distance [PORT]"')
else:
    print(f'ПРОПУЩЕНО (найдено {src.count(old_text)}): сокращение подписи')

# 2. Add two simple no-argument blocks right after the existing getDistance block entry
anchor_block = """                {
                    opcode: 'getDistance',
                    text: formatMessage({
                        id: 'wedo2.getDistance',
                        default: 'distance [PORT]',
                        description: 'the value returned by the distance sensor'
                    }),
                    blockType: BlockType.REPORTER,
                    arguments: {
                        PORT: {
                            type: ArgumentType.STRING,
                            menu: 'PORT',
                            defaultValue: WeDo2PortLabel.A
                        }
                    }
                },"""

new_blocks = """                {
                    opcode: 'getDistanceA',
                    text: 'distance (A)',
                    blockType: BlockType.REPORTER
                },
                {
                    opcode: 'getDistanceB',
                    text: 'distance (B)',
                    blockType: BlockType.REPORTER
                },"""

if src.count(anchor_block) == 1:
    src = src.replace(anchor_block, anchor_block + "\n" + new_blocks)
    print('OK: добавлены простые блоки "distance (A)" / "distance (B)" с галочкой')
else:
    print(f'ПРОПУЩЕНО (найдено {src.count(anchor_block)}): вставка простых блоков distance A/B')

# 3. Add matching class methods right after getDistance(args) method
anchor_method = """    getDistance (args) {
        const port = args.PORT === WeDo2PortLabel.B ? 1 : 0;
        return this._peripheral.distance(port);
    }"""

new_methods = """

    getDistanceA () {
        return this._peripheral.distance(0);
    }

    getDistanceB () {
        return this._peripheral.distance(1);
    }"""

if src.count(anchor_method) == 1:
    src = src.replace(anchor_method, anchor_method + new_methods)
    print('OK: добавлены методы getDistanceA() / getDistanceB()')
else:
    print(f'ПРОПУЩЕНО (найдено {src.count(anchor_method)}): вставка методов')

open(path, 'w', encoding='utf-8').write(src)
print('Файл сохранён.')