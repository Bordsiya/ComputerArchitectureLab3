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
- `port` = передача данных в процессор реализовано через команды (`IN`, `OUTC`, `OUT`)
- `prob1` = задача Эйлера №1 - найти сумму чисел, кратных 3 и 5, которые меньше 1000

## Язык программирования ##
Типизация: сильная статическая

Язык: упрощенный `javascript`
- Типы: `int`/`string`
- `if (comparison) ... endif`
- `while (comparison) ... endwhile`
- `print(variable, type)` = передает значение переменной в выходной буфер, type определяет как выводить переменную - интерпретируя данные как char или нет
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

<print_statement> ::= "print" "(" <ident> "," "int" ")" <nl_block> | "print" "(" <ident> "," "string" ")" <nl_block>
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
print(sum, int)
```

```js
// Hello world program
string hw = "hello world!"
print(hw, string)
```

## Организация памяти ##
Модель памяти процессора: 
- структура памяти однородная, запись на порт осуществляется посредством отдельных команд
- каждая инструкция занимает 1 машинное слово
- машинное слово - 32 бита, знаковое
- строки, объявленные пользователем распеделяются по памяти один символ на ячейку

## Система команд ##
### Особенности процессора ###
- Машинное слово - 32 бита, знаковое
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
- Ввод-вывод - port-mapped. Осуществляется посредством взаимодействия регистра `IO` с регистром `ACC`/с портами ввода-вывода

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
			ACC + DR -> ACC
		</td>
	</tr>
	<tr>
		<td>SUB</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			ACC - DR -> ACC
		</td>
	</tr>
	<tr>
		<td>DIV</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			ACC // DR -> ACC
		</td>
	</tr>
	<tr>
		<td>MUL</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			ACC * DR -> ACC
		</td>
	</tr>
	<tr>
		<td>MOD</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			ACC % DR -> ACC
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
			Если DR > 0: PC + 1 -> PC
		</td>
	</tr>
	<tr>
		<td>LD</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			0 + DR -> ACC
		</td>
	</tr>
	<tr>
		<td>ST</td>
		<td>2</td>
		<td>
			Execution
		</td>
		<td>
			M -> AR; ACC -> MEM[AR]
		</td>
	</tr>
	<tr>
		<td>JMP</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			DR -> PC
		</td>
	</tr>
	<tr>
		<td>BEQ</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			Если z == 1: DR -> PC
		</td>
	</tr>
	<tr>
		<td>BNE</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			Если z == 0: DR -> PC
		</td>
	</tr>
	<tr>
		<td>BGE</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			Если n == 0: DR -> PC
		</td>
	</tr>
	<tr>
		<td>BLE</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			Если z v n == 1: DR -> PC
		</td>
	</tr>
	<tr>
		<td>BL</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			Если n == 1: DR -> PC
		</td>
	</tr>
	<tr>
		<td>BG</td>
		<td>1</td>
		<td>
			Operand/Execution
		</td>
		<td>
			Если z v n == 0: DR -> PC
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
			0 -> ACC
		</td>
	</tr>
	<tr>
		<td>IN</td>
		<td>1</td>
		<td>
			Execution
		</td>
		<td>
			IO -> ACC
		</td>
	</tr>
	<tr>
		<td>OUTC</td>
		<td>1</td>
		<td>
			Execution
		</td>
		<td>
			chr(ACC) -> IO
		</td>
	</tr>
	<tr>
		<td>OUT</td>
		<td>1</td>
		<td>
			Execution
		</td>
		<td>
			ACC -> IO
		</td>
	</tr>
	<tr>
		<td>INC</td>
		<td>2</td>
		<td>
			Execution
		</td>
		<td>
			1 -> DR; ACC + DR -> ACC
		</td>
	</tr>
	<tr>
		<td>DEC</td>
		<td>2</td>
		<td>
			Execution
		</td>
		<td>
			-1 -> DR; ACC + DR -> ACC
		</td>
	</tr>
	<tr>
		<td>NEG</td>
		<td>2</td>
		<td>
			Execution
		</td>
		<td>
			-1 -> DR; ACC * DR -> ACC
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
		<td>M -> DR</td>
		<td>1</td>
	</tr>
	<tr>
		<td>ABSOLUTE</td>
		<td>MEM[M] -> DR</td>
		<td>2</td>
	</tr>
	<tr>
		<td>RELATIVE</td>
		<td>MEM[МEM[M]] -> DR</td>
		<td>4</td>
	</tr>
</table>


### Кодирование инструкций ###
- Машинный код сериализуется в список JSON
- Один элемент списка - 1 инструкция
- Индекс списка - адрес инструкции

Примеры:
- DATA
```json
{
        "opcode": "DATA",
        "arg": 0,
        "arg_mode": "DIRECT"
    }
```
- Addressed command
```json
{
        "opcode": "LD",
        "arg": 13,
        "arg_mode": "ABSOLUTE"
    }
```
- Unaddressed command
```json
{
        "opcode": "HLT"
    }
```
- `opcode` = код операции
- `arg` = адрес аргумента операции
- `arg_mode` = режим адресации

## Транслятор ##
Реализован в [translator](https://github.com/Bordsiya/ComputerArchitectureLab3/tree/master/translator)

Интерфейс командной строки: `translate.py <input_file> <target_file>`

Этапы трансляции:
- Анализ кода с помощью Lexer'а: 
	- разбор кода на токены
	- выявление ошибок
- Парсинг токенов с помощью Parser'а в соответствии с BNF:
	- выявление ошибок
	- преобразование комбинаций токенов в последовательности из Term'ов
	- добавление/обновление необходимых переменных и лейблов с запоминаением их адресов
	- после обработки исходного кода - соединение переменных/лейблов и инструкций воедино (переподсчет адресов, замена названий аргументов на соответвующие адреса)

### Пример ###
```js
// Hello world program
string hw = "hello world!"
print(hw, string)
```

Состояние преобразованного кода до переподсчета адресов можно для улучшения понимания рассматривать как:
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
        "arg": 1,
        "arg_mode": "ABSOLUTE"
    },
    {
        "opcode": "DATA",
        "arg": 72,
        "arg_mode": "DIRECT"
    },
    {
        "opcode": "DATA",
        "arg": 101,
        "arg_mode": "DIRECT"
    },
    {
        "opcode": "DATA",
        "arg": 108,
        "arg_mode": "DIRECT"
    },
    {
        "opcode": "DATA",
        "arg": 108,
        "arg_mode": "DIRECT"
    },
    {
        "opcode": "DATA",
        "arg": 111,
        "arg_mode": "DIRECT"
    },
    {
        "opcode": "DATA",
        "arg": 32,
        "arg_mode": "DIRECT"
    },
    {
        "opcode": "DATA",
        "arg": 119,
        "arg_mode": "DIRECT"
    },
    {
        "opcode": "DATA",
        "arg": 111,
        "arg_mode": "DIRECT"
    },
    {
        "opcode": "DATA",
        "arg": 114,
        "arg_mode": "DIRECT"
    },
    {
        "opcode": "DATA",
        "arg": 108,
        "arg_mode": "DIRECT"
    },
    {
        "opcode": "DATA",
        "arg": 100,
        "arg_mode": "DIRECT"
    },
    {
        "opcode": "DATA",
        "arg": 33,
        "arg_mode": "DIRECT"
    },
    {
        "opcode": "DATA",
        "arg": 0,
        "arg_mode": "DIRECT"
    },
    {
        "opcode": "LD",
        "arg": 0,
        "arg_mode": "RELATIVE"
    },
    {
        "opcode": "BEQ",
        "arg": 21,
        "arg_mode": "DIRECT"
    },
    {
        "opcode": "OUTC"
    },
    {
        "opcode": "LD",
        "arg": 0,
        "arg_mode": "ABSOLUTE"
    },
    {
        "opcode": "INC"
    },
    {
        "opcode": "ST",
        "arg": 0,
        "arg_mode": "ABSOLUTE"
    },
    {
        "opcode": "JUMP",
        "arg": 14,
        "arg_mode": "DIRECT"
    },
    {
        "opcode": "HLT"
    }
]
```

## Модель процессора ##
Реализован в [machine](https://github.com/Bordsiya/ComputerArchitectureLab3/tree/master/machine)

Интерфейс командной строки: `machinery.py <code_file> <input_file>`
### Схема DataPath и ControlUnit ###
![processor_model_4](https://user-images.githubusercontent.com/22819920/221947314-d17ca1b1-aeba-4c07-a5de-65ee9b8bfb3a.png)
ControlUnit:
- Hardwired (реализован полностью на python)
- Моделирование на уровне инструкций
- Instruction Decoder - декодировщик инструкций и установщик сигналов

Сигналы (обрабатываются за 1 такт, реализованы в виде методов класса):
- latch_acc - защелкнуть выбранное значение в `ACC`
- latch_dr - защелкнуть выбранное значение в `DR`
- latch_ar - защелкнуть выбранное значение в `AR`
- latch_program_counter - сигнал для обновления счётчика команд `PC`

Флаги:
- Z (Zero) - отражает наличие нулевого значения в `ACC`
- N (Negative) - отражает наличие отрицательного значения в `ACC`

Особенности работы модели:
- Для журнала состояний используется стандартный модуль `logging`
- Количество инструкций для моделирования ограничено hardcoded константой
- Управление симуляцией организовано в функции `simulate`
- Остановка симуляции осуществляется при помощи исключений:
	- `StopIteration` = при достижении `HLT` инструкции
	- `MachineException` = при возникновении рантайм-ошибок (деление на 0, слишком большая программа, слишком долгое исполнение и т.д.)
	- `EOFException` = при ошибке `Buffer is empty`

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
	<td>48</td>
	<td>136</td>
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
