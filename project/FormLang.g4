grammar FormLang;

// lexems

IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;
WS: [ \r\n\t]+ -> skip;
ST_END: ';';
fragment INT: ([0-9]+);
fragment FLOAT: ([0-9]* '.' [0-9]+);
NUMBER: INT | FLOAT;
fragment STRING_W: '"' .*? '"';
fragment STRING_S: '\'' .*? '\'';
fragment STRING_T: '`' .*? '`';
STRING: STRING_W | STRING_S | STRING_T;
COMMENT: '#' ~( '\r' | '\n' )* -> skip;


// grammar

prog: (stmt ST_END)* ;

stmt: assignment
    | print
    ;

print: 'show' expr;

var: IDENTIFIER;
val: NUMBER                     # Number
   | STRING                     # String
   | '{' expr (',' expr)* '}'   # Set     // множество
   | '(' expr ',' expr ')'      # Tuple   // пара
   | '{' NUMBER '..' NUMBER '}' # Range
   ;


assignment: var 'is' expr
          | var 'is' lambda
          ;

expr: val                             // переменные
    | var                             // константы
    | expr '||>' expr                 // задать множество стартовых состояний
    | expr '||:' expr                 // задать множество финальных состояний
    | expr '|>' expr                  // добавить состояния в множество стартовых
    | expr '|:' expr                  // добавить состояния в множество финальных
    | expr 'get' 'starts'             // получить множество стартовых состояний
    | expr 'get' 'finals'             // получить множество финальных состояний
    | expr 'get' 'reachable'          // получить все пары достижимых вершин
    | expr 'get' 'vertices'           // получить все вершины
    | expr 'get' 'edges'              // получить все рёбра
    | expr 'get' 'lables'             // получить все метки
    | expr 'map' lambda               // классический map
    | expr 'filter' lambda            // классический filter
    | 'load' STRING                   // загрузка графа
    | expr '&' expr                   // пересечение языков
    | expr '.' expr                   // конкатенация языков
    | expr '|' expr                   // объединение языков
    | expr '*'                        // замыкание языков (звезда Клини)
    | expr 'smb' expr                 // единичный переход
    | expr '[' (STRING | NUMBER) ']'  // доступ к полям
    | expr 'in' expr                  // содержится в
    | '(' expr ')'
    ;

lambda: '/' var '->' expr '/';
