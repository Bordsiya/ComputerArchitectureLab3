# Архитектура компьютера. Лабораторная работа №3 #

Бордун А.В.

## Вариант ##
`alg | acc | neum | hw | instr | struct | stream | port | prob1`

- `alg` = `javascript`-подобный язык
- `acc` = все вычисления построены вокруг регистра `ACC`, выполняющего роль аккумулятора
- `neum` = команды и данные хранятся в общей памяти
- `hw` = `Control Unit` реализован как часть модели, микрокода нет
- `instr` = каждая инструкция расписана потактово, но в журнале фиксируется только результат выполнения
- `struct` = инструкции представляются в виде высокоуровневой структуры
- `stream` = ввод-вывод реализован как поток данных
- `port` = передача данных в процессор реализовано через команды (`IN`, `OUT`)
- `prob1` = задача Эйлера №1 - найти сумму чисел, кратных 3 и 5, которые меньше 1000

## Язык программирования ##
Типизация: сильная статическая

Язык: упрощенный `javascript`
- Типы: `int`/`string`
- `if (comparison) ... endif`
- `while (comparison) ... endwhile`
- `print(variable)` = передает значение переменной в выходной буфер
- `input(variable)` = считывает значение из входного буфера в переменную
- Ветвления: >=, <=, ==, <, >, !=
- Математические операции: 
  - term + term
  - term - term
  - unary / unary
  - unary * unary
  - unary % unary
- Поддерживаются также обозначения положительных/отрицательных чисел как: +primary/-primary
- Поддерживаемые присваивания:
  - variable = expression
  - variable += expression
  - variable -= expression
  - variable /= expression
  - variable *= expression
  - variable %= expression
- Аргументами математических операций могут выступать литералы типа `int` и переменные типа `int`
- Поддерживаются только целые числа
- Поддерживаются комментарии в формате: // comment

### BNF ###
```ebnf
<program> ::= <block_of_statements>
<block_of_statements> ::= <statement> <block_of_statements> | <statement>
<statement> ::= <print_statement> | <input_statement> | <if_statement> | <while_statement> | <int_declaration> 
  | <string_declaration> | <variable_assignment> | <comment_statement>

<print_statement> ::= "print" "(" <ident> ")" <nl_block>
<input_statement> ::= "input" "(" <ident> ")" <nl_block>
<if_statement> ::= "if" "(" <comparison> ")" <nl_block> <block_of_statements> "endif" <nl_block>
<while_statement> ::= "while" "(" <comparison> ")" <nl_block> <block_of_statements> "endwhile" <nl_block>
<int_declaration> ::= "int" <ident> "=" <expression> <nl_block>
<string_declaration> ::= "string" <ident> "=" <word> <nl_block>
<variable_assignment> ::= <ident> "=" <expression> <nl_block> | <ident> "+=" <expression> <nl_block> 
  | <ident> "-=" <expression> <nl_block> | <ident> "/=" <expression> <nl_block> | <ident> "*=" <expression> <nl_block> 
  | <ident> "%=" <expression> <nl_block>
<comment_statement> ::= "//" <word> <nl_block>

<nl_block> ::= <nl> <nl_block> | <nl>
<nl> ::= '\n'
<comparison> ::= <expression> | <expression> "==" <expression> | <expression> "!=" <expression> | <expression> ">" <expression> | 
  <expression> "<" <expression>  |<expression> ">=" <expression> | <expression> "<=" <expression>
<expression> ::= <term> | <term> "+" <term> | <term> "-" <term>
<term> ::= <unary> | <unary> "/" <unary> | <unary> "*" <unary> | <unary> "%" <unary>
<unary> ::= <primary> | "+"<primary> | "-"<primary>
<primary> ::= <number> | <ident>

<ident> ::= <letter> | <letter> <letter_or_digit_list>
<number> ::= <digit> | <digit_from_1> <digit_list>
<word> ::= <letter_or_digit_or_space> | <letter_or_digit_or_space> <word>

<letter_or_digit_list> ::= <letter_or_digit> | <letter_or_digit> <letter_or_digit_list>
<digit_list> ::= <digit> <digit_list> | <digit>
<letter_or_digit_or_space_list> ::= <letter_or_digit_or_space> | <letter_or_digit_or_space> <letter_or_digit_or_space_list>

<letter_or_digit> ::= <letter> | <digit>
<letter_or_digit_or_space> ::= <letter> | <digit> | <space>
<space> ::= " " | "\t"
<letter> ::= [a-z] | [A-Z]
<digit> ::= [0-9]
<digit_from_1> ::= [1-9]
```

### Примеры ###
```js
// Euler 1 problem
int sum = 0
int i = 0
while (i < 1000)
	if (i % 3 == 0)
	    if (i % 5 == 0)
	        sum += 1
	    endif
	endif
	i += 1
endwhile
print(sum)
```

```js
// Hello world program
string hw = "hello world!"
print(hw)
```

## Транслятор ##
Реализован в [translator](https://github.com/Bordsiya/ComputerArchitectureLab3/tree/master/translator)

Интерфейс командной строки: `translate.py <input_file> <target_file>`

Этапы трансляции:
- Анализ кода с помощью Lexer'а: разбор кода на токены, выявления ошибок
- Парсинг токенов с помощью Parser'а в соответствии с BNF, выявление ошибок: преобразование комбинаций токенов в последовательности из Term'ов, добавление/обновление необходимых переменных и лейблов, после обработки кода - соединение переменных/лейблов и инструкций воедино (переподсчет адресов, замена названий аргументов на соответвующие адреса)

### Пример ###
```js
// Hello world program
string hw = "hello world!"
print(hw)
```

Состояние преобразованного кода до переподсчета адресов можно для простоты рассматривать как:
```asm
hwptr: hw
hw: 
68
65
6C
6C
6F
20
77
6F
72
6C
64
21
0
start: 
loop1: LD (hwptr)
BEQ $end_loop1
OUT
LD $hwptr
INC
ST $hwptr
JUMP $loop1
end_loop1: 
HLT
```

После соединения переменных/лейблов и инструкций, преобразования в Term'ы, переподсчета адресов и замены аргументов на их адреса:
```json
[
    {
        "opcode": "DATA",
        "term": [
            0,
            1,
            "ABSOLUTE"
        ]
    },
    {
        "opcode": "DATA",
        "term": [
            1,
            104,
            "DIRECT"
        ]
    },
    {
        "opcode": "DATA",
        "term": [
            2,
            101,
            "DIRECT"
        ]
    },
    {
        "opcode": "DATA",
        "term": [
            3,
            108,
            "DIRECT"
        ]
    },
    {
        "opcode": "DATA",
        "term": [
            4,
            108,
            "DIRECT"
        ]
    },
    {
        "opcode": "DATA",
        "term": [
            5,
            111,
            "DIRECT"
        ]
    },
    {
        "opcode": "DATA",
        "term": [
            6,
            32,
            "DIRECT"
        ]
    },
    {
        "opcode": "DATA",
        "term": [
            7,
            119,
            "DIRECT"
        ]
    },
    {
        "opcode": "DATA",
        "term": [
            8,
            111,
            "DIRECT"
        ]
    },
    {
        "opcode": "DATA",
        "term": [
            9,
            114,
            "DIRECT"
        ]
    },
    {
        "opcode": "DATA",
        "term": [
            10,
            108,
            "DIRECT"
        ]
    },
    {
        "opcode": "DATA",
        "term": [
            11,
            100,
            "DIRECT"
        ]
    },
    {
        "opcode": "DATA",
        "term": [
            12,
            33,
            "DIRECT"
        ]
    },
    {
        "opcode": "DATA",
        "term": [
            13,
            0,
            "DIRECT"
        ]
    },
    {
        "opcode": "LD",
        "term": [
            14,
            0,
            "RELATIVE"
        ]
    },
    {
        "opcode": "BEQ",
        "term": [
            15,
            21,
            "DIRECT"
        ]
    },
    {
        "opcode": "OUT",
        "term": [
            16,
            0,
            "DIRECT"
        ]
    },
    {
        "opcode": "LD",
        "term": [
            17,
            0,
            "ABSOLUTE"
        ]
    },
    {
        "opcode": "INC",
        "term": [
            18,
            0,
            "DIRECT"
        ]
    },
    {
        "opcode": "ST",
        "term": [
            19,
            0,
            "ABSOLUTE"
        ]
    },
    {
        "opcode": "JUMP",
        "term": [
            20,
            14,
            "DIRECT"
        ]
    },
    {
        "opcode": "HLT",
        "term": [
            21,
            0,
            "DIRECT"
        ]
    }
]
```

## Система команд ##
### Особенности ###
- Машинное слово = 32 бита, знаковое
- Память:
	- адресуется через регистр `AR`
	- может быть прочитана в регистр `DR`
	- может быть записана из регистра `ACC`
- ALU:
	- поддерживаемые операции: сложение/вычитание/деление/умножение/взятие остатка от деления
	- на левый вход принимает `ACC`
	- на правый вход принимает `DR`
	- по результату операции выставляет флаги: N и Z
- `PC` = счетчик команд: инкрементируется после каждой инструкции или перезаписывается инструкцией перехода
- Прерываний нет
- Ввод-вывод - port-mapped. Осуществляется посредством взаимодействия регистра `IO` с регистром `ACC`

### Набор инструкций ###
<table>
	<tr>
		<td>Syntax</td>
		<td>Кол-во тактов</td>
		<td>Циклы</td>
		<td>Comment</td>
	</tr>
	<tr>
		<td>ADD</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			ACC -> ACC + DR
		</td>
	</tr>
	<tr>
		<td>SUB</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			ACC -> ACC - DR
		</td>
	</tr>
	<tr>
		<td>DIV</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			ACC -> ACC / DR
		</td>
	</tr>
	<tr>
		<td>MUL</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			ACC -> ACC * DR
		</td>
	</tr>
	<tr>
		<td>MOD</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			ACC -> ACC % DR
		</td>
	</tr>
	<tr>
		<td>CMP</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			Установить флаги по результату ACC - DR
		</td>
	</tr>
	<tr>
		<td>LOOP</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			Если DR > 0: PC -> PC + 1
		</td>
	</tr>
	<tr>
		<td>LD</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			ACC -> 0 + DR
		</td>
	</tr>
	<tr>
		<td>ST</td>
		<td>2</td>
		<td>
			Execution
		</td>
		<td>
			AR -> M; MEM[AR] -> ACC
		</td>
	</tr>
	<tr>
		<td>JMP</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			PC -> DR
		</td>
	</tr>
	<tr>
		<td>BEQ</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			Если z == 1: PC -> DR
		</td>
	</tr>
	<tr>
		<td>BNE</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			Если z == 0: PC -> DR
		</td>
	</tr>
	<tr>
		<td>BGE</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			Если n == 0: PC -> DR
		</td>
	</tr>
	<tr>
		<td>BLE</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			Если z v n == 1: PC -> DR
		</td>
	</tr>
	<tr>
		<td>BL</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			Если n == 1: PC -> DR
		</td>
	</tr>
	<tr>
		<td>BG</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			Если z v n == 0: PC -> DR
		</td>
	</tr>
	<tr>
		<td>NOP</td>
		<td>0</td>
		<td>
			Execution
		</td>
		<td>
			Нет операции
		</td>
	</tr>
	<tr>
		<td>HLT</td>
		<td>0</td>
		<td>
			Execution
		</td>
		<td>
			Останов
		</td>
	</tr>
	<tr>
		<td>CLA</td>
		<td>1</td>
		<td>
			Execution
		</td>
		<td>
			ACC -> 0
		</td>
	</tr>
	<tr>
		<td>IN</td>
		<td>1</td>
		<td>
			Execution
		</td>
		<td>
			ACC -> IO
		</td>
	</tr>
	<tr>
		<td>OUT</td>
		<td>1</td>
		<td>
			Execution
		</td>
		<td>
			IO -> ACC
		</td>
	</tr>
	<tr>
		<td>INC</td>
		<td>2</td>
		<td>
			Execution
		</td>
		<td>
			DR -> 1; ACC -> ACC + DR
		</td>
	</tr>
	<tr>
		<td>DEC</td>
		<td>2</td>
		<td>
			Execution
		</td>
		<td>
			DR -> -1; ACC -> ACC + DR
		</td>
	</tr>
	<tr>
		<td>NEG</td>
		<td>2</td>
		<td>
			Execution
		</td>
		<td>
			DR -> -1; ACC -> ACC * DR
		</td>
	</tr>
</table>

### Циклы ###
- Operand Fetch
- Execution Fetch

### Режимы адресации ###
<table>
	<tr>
		<td>Режим</td>
		<td>Comment</td>
		<td>Кол-во тактов</td>
	</tr>
	<tr>
		<td>DIRECT</td>
		<td>DR -> M</td>
		<td>1</td>
	</tr>
	<tr>
		<td>ABSOLUTE</td>
		<td>DR -> MEM[M]</td>
		<td>2</td>
	</tr>
	<tr>
		<td>RELATIVE</td>
		<td>DR -> MEM[МEM[M]]</td>
		<td>4</td>
	</tr>
</table>


### Кодирование инструкций ###
- Машинный код хранится в виде JSON-списка
- Каждый элемент состоит из `opcode` и `term`

Примеры:
- DATA
```json
{
        "opcode": "DATA",
        "term": [
            1,
            0,
            "DIRECT"
        ]
    }
```
- Addressed command
```json
{
        "opcode": "LD",
        "term": [
            14,
            13,
            "ABSOLUTE"
        ]
    }
```
- Unaddressed command
```json
{
        "opcode": "IN",
        "term": [
            14,
            0,
            "DIRECT"
        ]
    }
```
- `opcode` = код операции
- `term` = описание операции
- `term[0]` = line
- `term[1]` = arg
- `term[2]` = arg_mode

## Модель процессора ##
Реализован в [machine](https://github.com/Bordsiya/ComputerArchitectureLab3/tree/master/machine1)

Интерфейс командной строки: `machinery.py <code_file> <input_file>`
### Схема DataPath и ControlUnit ###
![processor_model_4](https://user-images.githubusercontent.com/22819920/221947314-d17ca1b1-aeba-4c07-a5de-65ee9b8bfb3a.png)
- Управление симуляцией организовано в функции `simulate`
- Остановка симуляции осуществляется при помощи исключений:
	- `StopIteration` = при достижении `HLT` инструкции
	- `MachineException` = при возникновении рантайм-ошибок (деление на 0, слишком большая программа, слишком долгое исполнение и т.д.)

## Апробация ##
TODO: тесты
<table>
<tr>
	<td>ФИО</td> 
	<td>алг</td> 
	<td>LoC</td> 
	<td>code байт</td> 
	<td>code инстр</td> 
	<td>инстр</td> 
	<td>такт</td> 
	<td>вариант</td>
</tr>
<tr>
	<td>Бордун А.В.</td> 
	<td>hello</td> 
	<td>3</td> 
	<td>-</td> 
	<td>22</td> 
	<td>100</td> 
	<td>274</td> 
	<td>alg | acc | neum | hw | instr | struct | stream | port | prob1</td>
</tr>
<tr>
	<td>Бордун А.В.</td>
	<td>cat</td>
	<td>7</td>
	<td>-</td>
	<td>18</td>
	<td>132</td>
	<td>381</td>
	<td>alg | acc | neum | hw | instr | struct | stream | port | prob1</td>
</tr>
<tr>
	<td>Бордун А.В.</td>
	<td>prob1</td>
	<td>12</td>
	<td>-</td>
	<td>59</td>
	<td>29366</td>
	<td>95141</td>
	<td>alg | acc | neum | hw | instr | struct | stream | port | prob1</td>
</tr>
</table>
