#!/usr/bin/env python3
import sys

path = sys.argv[1] if len(sys.argv) > 1 else 'src/vm/extensions/block/index.js'
hub_label = sys.argv[2] if len(sys.argv) > 2 else '3'

src = open(path, encoding='utf-8').read()
orig = src

def replace_once(old, new, label):
    global src
    count = src.count(old)
    if count != 1:
        print(f'ПРОПУЩЕНО ({count} совпадений, ожидалось 1): {label}')
        return
    src = src.replace(old, new, 1)
    print(f'OK: {label}')

def replace_all(old, new, label, expected):
    global src
    count = src.count(old)
    if count != expected:
        print(f'ПРОПУЩЕНО ({count} совпадений, ожидалось {expected}): {label}')
        return
    src = src.replace(old, new)
    print(f'OK ({expected}x): {label}')

# 1. this._sensors init -> arrays (2 occurrences: constructor + reset())
replace_all(
"""        this._sensors = {
            tiltX: 0,
            tiltY: 0,
            distance: 0
        };""",
"""        this._sensors = {
            tiltX: [0, 0],
            tiltY: [0, 0],
            distance: [0, 0]
        };""",
    'this._sensors init -> arrays', 2
)

# 2. getters -> methods with port argument
replace_once(
"""    get tiltX () {
        return this._sensors.tiltX;
    }""",
"""    tiltX (port = 0) {
        return this._sensors.tiltX[port];
    }""",
    'get tiltX -> tiltX(port)'
)

replace_once(
"""    get tiltY () {
        return this._sensors.tiltY;
    }""",
"""    tiltY (port = 0) {
        return this._sensors.tiltY[port];
    }""",
    'get tiltY -> tiltY(port)'
)

replace_once(
"""    get distance () {
        return this._sensors.distance;
    }""",
"""    distance (port = 0) {
        return this._sensors.distance[port];
    }""",
    'get distance -> distance(port)'
)

# 3. _onMessage: store by port
replace_once(
"""            if (type === WeDo2Device.DISTANCE) {
                this._sensors.distance = data[2];
            }
            if (type === WeDo2Device.TILT) {
                this._sensors.tiltX = data[2];
                this._sensors.tiltY = data[3];
            }""",
"""            if (type === WeDo2Device.DISTANCE) {
                this._sensors.distance[connectID - 1] = data[2];
            }
            if (type === WeDo2Device.TILT) {
                this._sensors.tiltX[connectID - 1] = data[2];
                this._sensors.tiltY[connectID - 1] = data[3];
            }""",
    '_onMessage: store value by port'
)

# 4. _clearPort: clear by port
replace_once(
"""        if (type === WeDo2Device.TILT) {
            this._sensors.tiltX = this._sensors.tiltY = 0;
        }
        if (type === WeDo2Device.DISTANCE) {
            this._sensors.distance = 0;
        }""",
"""        if (type === WeDo2Device.TILT) {
            this._sensors.tiltX[connectID - 1] = 0;
            this._sensors.tiltY[connectID - 1] = 0;
        }
        if (type === WeDo2Device.DISTANCE) {
            this._sensors.distance[connectID - 1] = 0;
        }""",
    '_clearPort: clear by port'
)

# 5. Block-class methods: accept PORT argument
replace_once(
"""    getDistance () {
        return this._peripheral.distance;
    }""",
"""    getDistance (args) {
        const port = args.PORT === WeDo2PortLabel.B ? 1 : 0;
        return this._peripheral.distance(port);
    }""",
    'getDistance(args) with PORT'
)

replace_once(
"""    isTilted (args) {
        return this._isTilted(args.TILT_DIRECTION_ANY);
    }""",
"""    isTilted (args) {
        const port = args.PORT === WeDo2PortLabel.B ? 1 : 0;
        return this._isTilted(args.TILT_DIRECTION_ANY, port);
    }""",
    'isTilted(args) with PORT'
)

replace_once(
"""    getTiltAngle (args) {
        return this._getTiltAngle(args.TILT_DIRECTION);
    }""",
"""    getTiltAngle (args) {
        const port = args.PORT === WeDo2PortLabel.B ? 1 : 0;
        return this._getTiltAngle(args.TILT_DIRECTION, port);
    }""",
    'getTiltAngle(args) with PORT'
)

# 6. _isTilted / _getTiltAngle: thread port through
replace_once(
"""    _isTilted (direction) {
        switch (direction) {
        case WeDo2TiltDirection.ANY:
            return this._getTiltAngle(WeDo2TiltDirection.UP) >= Scratch3WeDo2Blocks.TILT_THRESHOLD ||
                this._getTiltAngle(WeDo2TiltDirection.DOWN) >= Scratch3WeDo2Blocks.TILT_THRESHOLD ||
                this._getTiltAngle(WeDo2TiltDirection.LEFT) >= Scratch3WeDo2Blocks.TILT_THRESHOLD ||
                this._getTiltAngle(WeDo2TiltDirection.RIGHT) >= Scratch3WeDo2Blocks.TILT_THRESHOLD;
        default:
            return this._getTiltAngle(direction) >= Scratch3WeDo2Blocks.TILT_THRESHOLD;
        }
    }""",
"""    _isTilted (direction, port = 0) {
        switch (direction) {
        case WeDo2TiltDirection.ANY:
            return this._getTiltAngle(WeDo2TiltDirection.UP, port) >= Scratch3WeDo2Blocks.TILT_THRESHOLD ||
                this._getTiltAngle(WeDo2TiltDirection.DOWN, port) >= Scratch3WeDo2Blocks.TILT_THRESHOLD ||
                this._getTiltAngle(WeDo2TiltDirection.LEFT, port) >= Scratch3WeDo2Blocks.TILT_THRESHOLD ||
                this._getTiltAngle(WeDo2TiltDirection.RIGHT, port) >= Scratch3WeDo2Blocks.TILT_THRESHOLD;
        default:
            return this._getTiltAngle(direction, port) >= Scratch3WeDo2Blocks.TILT_THRESHOLD;
        }
    }""",
    '_isTilted(direction, port)'
)

replace_once(
"""    _getTiltAngle (direction) {
        switch (direction) {
        case WeDo2TiltDirection.UP:
            return this._peripheral.tiltY > 45 ? 256 - this._peripheral.tiltY : -this._peripheral.tiltY;
        case WeDo2TiltDirection.DOWN:
            return this._peripheral.tiltY > 45 ? this._peripheral.tiltY - 256 : this._peripheral.tiltY;
        case WeDo2TiltDirection.LEFT:
            return this._peripheral.tiltX > 45 ? 256 - this._peripheral.tiltX : -this._peripheral.tiltX;
        case WeDo2TiltDirection.RIGHT:
            return this._peripheral.tiltX > 45 ? this._peripheral.tiltX - 256 : this._peripheral.tiltX;
        default:
            log.warn(`Unknown tilt direction in _getTiltAngle: ${direction}`);
        }
    }""",
"""    _getTiltAngle (direction, port = 0) {
        const tiltY = this._peripheral.tiltY(port);
        const tiltX = this._peripheral.tiltX(port);
        switch (direction) {
        case WeDo2TiltDirection.UP:
            return tiltY > 45 ? 256 - tiltY : -tiltY;
        case WeDo2TiltDirection.DOWN:
            return tiltY > 45 ? tiltY - 256 : tiltY;
        case WeDo2TiltDirection.LEFT:
            return tiltX > 45 ? 256 - tiltX : -tiltX;
        case WeDo2TiltDirection.RIGHT:
            return tiltX > 45 ? tiltX - 256 : tiltX;
        default:
            log.warn(`Unknown tilt direction in _getTiltAngle: ${direction}`);
        }
    }""",
    '_getTiltAngle(direction, port)'
)

# 7. Add WeDo2PortLabel enum right after WeDo2MotorLabel = {
idx = src.find('const WeDo2MotorLabel = {')
if idx == -1:
    print('ПРОПУЩЕНО: не нашли WeDo2MotorLabel для вставки WeDo2PortLabel')
else:
    end = src.find('\n};', idx) + len('\n};')
    insertion = (
        "\n\nconst WeDo2PortLabel = {\n"
        "    A: 'A',\n"
        "    B: 'B'\n"
        "};"
    )
    src = src[:end] + insertion + src[end:]
    print('OK: добавлен const WeDo2PortLabel')

# 8. Add PORT argument + menu to getDistance / isTilted / getTiltAngle blocks in getInfo()
replace_once(
"""                {
                    opcode: 'getDistance',
                    text: formatMessage({
                        id: 'wedo2.getDistance',
                        default: 'distance',
                        description: 'the value returned by the distance sensor'
                    }),
                    blockType: BlockType.REPORTER
                },""",
"""                {
                    opcode: 'getDistance',
                    text: formatMessage({
                        id: 'wedo2.getDistance',
                        default: 'distance on port [PORT]',
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
                },""",
    'getDistance block: + PORT argument'
)

replace_once(
"""                {
                    opcode: 'isTilted',
                    text: formatMessage({
                        id: 'wedo2.isTilted',
                        default: 'tilted [TILT_DIRECTION_ANY]?',
                        description: 'whether the tilt sensor is tilted'
                    }),
                    blockType: BlockType.BOOLEAN,
                    arguments: {
                        TILT_DIRECTION_ANY: {
                            type: ArgumentType.STRING,
                            menu: 'TILT_DIRECTION_ANY',
                            defaultValue: WeDo2TiltDirection.ANY
                        }
                    }
                },""",
"""                {
                    opcode: 'isTilted',
                    text: formatMessage({
                        id: 'wedo2.isTilted',
                        default: 'tilted [TILT_DIRECTION_ANY] on port [PORT]?',
                        description: 'whether the tilt sensor is tilted'
                    }),
                    blockType: BlockType.BOOLEAN,
                    arguments: {
                        TILT_DIRECTION_ANY: {
                            type: ArgumentType.STRING,
                            menu: 'TILT_DIRECTION_ANY',
                            defaultValue: WeDo2TiltDirection.ANY
                        },
                        PORT: {
                            type: ArgumentType.STRING,
                            menu: 'PORT',
                            defaultValue: WeDo2PortLabel.A
                        }
                    }
                },""",
    'isTilted block: + PORT argument'
)

replace_once(
"""                {
                    opcode: 'getTiltAngle',
                    text: formatMessage({
                        id: 'wedo2.getTiltAngle',
                        default: 'tilt angle [TILT_DIRECTION]',
                        description: 'the angle returned by the tilt sensor'
                    }),
                    blockType: BlockType.REPORTER,
                    arguments: {
                        TILT_DIRECTION: {
                            type: ArgumentType.STRING,
                            menu: 'TILT_DIRECTION',
                            defaultValue: WeDo2TiltDirection.UP
                        }
                    }
                }
            ],""",
"""                {
                    opcode: 'getTiltAngle',
                    text: formatMessage({
                        id: 'wedo2.getTiltAngle',
                        default: 'tilt angle [TILT_DIRECTION] on port [PORT]',
                        description: 'the angle returned by the tilt sensor'
                    }),
                    blockType: BlockType.REPORTER,
                    arguments: {
                        TILT_DIRECTION: {
                            type: ArgumentType.STRING,
                            menu: 'TILT_DIRECTION',
                            defaultValue: WeDo2TiltDirection.UP
                        },
                        PORT: {
                            type: ArgumentType.STRING,
                            menu: 'PORT',
                            defaultValue: WeDo2PortLabel.A
                        }
                    }
                }
            ],""",
    'getTiltAngle block: + PORT argument'
)

# 9. Add PORT menu definition right after "menus: {"
replace_once(
"""            menus: {
                MOTOR_ID: {""",
"""            menus: {
                PORT: {
                    acceptReporters: true,
                    items: [
                        {text: 'port A', value: WeDo2PortLabel.A},
                        {text: 'port B', value: WeDo2PortLabel.B}
                    ]
                },
                MOTOR_ID: {""",
    'PORT menu added'
)

# 10. Hub-number prefix on every block's text, right before getInfo()'s return
replace_once(
"    getInfo () {\n        return {",
"    getInfo () {\n        const info = {",
    'getInfo(): return -> const info ='
)

if src.count('const info = {') == 1:
    # find the matching closing of getInfo's object literal -> it ends with "\n        };\n    }\n" after menus
    # We instead just locate the end of getInfo method body: the next "\n    }\n\n" after "const info = {"
    start = src.find('const info = {')
    # find "\n            }\n        };\n    }" pattern isn't reliable; use original closing we know: menus object ends with "\n            }\n        };\n    }\n" right after the WeDo2 menus block.
    marker = "\n        };\n    }\n"
    end = src.find(marker, start)
    if end == -1:
        print('ПРОПУЩЕНО: не нашли конец getInfo() для вставки return info')
    else:
        insertion = (
            f"\n\n        info.blocks.forEach(block => {{\n"
            f"            if (block.text) {{\n"
            f"                block.text = '{hub_label}| ' + block.text;\n"
            f"            }}\n"
            f"        }});\n"
            f"        return info;\n    }}\n"
        )
        src = src[:end] + insertion + src[end + len(marker):]
        print(f'OK: добавлена нумерация блоков (префикс "{hub_label}| ") и return info')

if src == orig:
    print('\nНичего не изменено — проверьте файл вручную.')
else:
    open(path, 'w', encoding='utf-8').write(src)
    print(f'\nГотово, файл {path} сохранён.')
