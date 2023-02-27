# Архитектура компьютера. Лабораторная работа №3 #

Бордун А.В.

## Вариант ##
`alg | acc | neum | hw | instr | struct | stream | port | prob1`

- `alg` = *javascript*-подобный язык
- `acc` = все вычисления построены вокруг регистра *ACC*, выполняющего роль аккумулятора
- `neum` = команды и данные хранятся в общей памяти
- `hw` = *Control Unit* реализован как часть модели, микрокода нет
- `instr` = каждая инструкция расписана потактово, но в журнале фиксируется только результат выполнения
- `struct` = инструкции представляются в виде высокоуровневой структуры
- `stream` = ввод-вывод реализован как поток данных
- `port` = передача данных в процессор реализовано через команды (*IN*, *OUT*)
- `prob1` = задача Эйлера №1 - найти сумму чисел, кратных 3 и 5, которые меньше 1000

## Язык программирования ##
Типизация: сильная статическая

Язык: упрощенный *javascript*
- Типы: *INT*/*STRING*
- *IF* (comparison) ... *ENDIF*
- *WHILE* (comparison) ... *ENDWHILE*
- *PRINT*(variable) = передает значение переменной в выходной буфер
- *INPUT*(variable) = считывает значение из входного буфера в переменную
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
- Аргументами математических операций могут выступать литералы типа *INT* и переменные типа *INT*
- Поддерживаются только целые числа
- Поддерживаются комментарии в формате: // comment

## BNF ##
```ebnf
<program> ::= <block_of_statements>
<block_of_statements> ::= <statement> <block_of_statements> | <statement>
<statement> ::= <print_statement> | <input_statement> | <if_statement> | <while_statement> | <int_declaration> 
  | <string_declaration> | <variable_assignment> | <comment_statement>

<print_statement> ::= "PRINT" "(" <ident> ")" <nl_block>
<input_statement> ::= "INPUT" "(" <ident> ")" <nl_block>
<if_statement> ::= "IF" "(" <comparison> ")" <nl_block> <block_of_statements> "ENDIF" <nl_block>
<while_statement> ::= "WHILE" "(" <comparison> ")" <nl_block> <block_of_statements> "ENDWHILE" <nl_block>
<int_declaration> ::= "INT" <ident> "=" <expression> <nl_block>
<string_declaration> ::= "STRING" <ident> "=" <word> <nl_block>
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
