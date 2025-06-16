// Test lexing of annotations with namespaces
OPENQASM 3.1;
@annotation
@annotation value
@annotation.long.namespace
@annotation.long.namespace  value
 @annotation.long.namespace
 @annotation.long.namespace  value
h q;
