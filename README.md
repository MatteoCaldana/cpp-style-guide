# C++ Style Guide
## Table of Contents
  - [Background](#background)
  - [Formatting code](#formatting-code)
  - [Static analysis](#static-analysis)
  - [File structure](#file-structure)
    - [Define guard](#define-guard)
    - [Includes](#includes)
  - [Namespaces](#namespaces)
  - [Variables](#variables)
    - [Local Variables](#local-variables)
    - [Global Variables](#global-variables)
      - [Common patterns](#common-patterns)
  - [Classes](#classes)
    - [Struct](#struct)
    - [Inheritance](#inheritance)
    - [Operator Overloading](#operator-overloading)
    - [Friends](#friends)
  - [Functions](#functions)
  - [Exceptions](#exceptions)
  - [Casting](#casting)
  - [Integer Types](#integer-types)
  - [Macros](#macros)
  - [Naming conventions](#naming-conventions)
    - [Types](#types)
    - [Variable prefixes](#variable-prefixes)
  - [Control structures](#control-structures)
    - [Switch](#switch)
  - [Pointers](#pointers)
  - [Return from errors immediately](#return-from-errors-immediately)

## Background
This document attempts to define a unified style for C++ programming.
It is heavily inspired by [Google Coding style for C++ code](https://google.github.io/styleguide/cppguide.html).

## Formatting code
- Format code automatically via clang-format and the provided `.clang-format` file.
- Use Unix-style linebreaks (`\n`), not Windows-style (`\r\n`).
- Each line of text in your code should be at most 80 characters long.
- Non-ASCII characters should be rare, and must use UTF-8 formatting.
- Use only spaces, and indent 2 spaces at a time.

## Static analysis
- Use `cpplint.py` to detect style errors. It is not perfect, and has both false positives and false negatives.
- Use `clang-tidy` to statically analyze the code:
```bash
cmake <options...> -DCMAKE_EXPORT_COMPILE_COMMANDS=ON <path>
run-clang-tidy -checks='google*,readability*,performance*,mpi*,cppcoreguidelines*,bugprone*,modernize-use-using,modernize-use-emplace,modernize-make-shared,modernize-make-unique' -use-color
```
- Use [Cppcheck](https://github.com/danmar/cppcheck) to statically analyze the code:
```bash
cmake <options...> -DCMAKE_EXPORT_COMPILE_COMMANDS=ON <path> 
cppcheck --project=compile_commands.json --check-level=exhaustive --inconclusive --enable=all
```


## File structure
In general, every header file (`.hpp`) should have an associated source file (`.cpp`). Header files should be self-contained (compile on their own). 
- Filenames should be all lowercase and can include underscores (`_`) 

### Define guard
All header files should have `#define` guards to prevent multiple inclusion. The format of the symbol name should be `<PROJECT>_<PATH>_<FILE>_H_`. To guarantee uniqueness, they should be based on the full path in a project's source tree. For example, the file `foo/src/bar/baz.h` in project foo should have the following guard:
```cpp
#ifndef FOO_BAR_BAZ_H_
#define FOO_BAR_BAZ_H_

...

#endif  // FOO_BAR_BAZ_H_
```

### Includes
Include headers in the following order: Related header, C system headers, C++ standard library headers, other libraries' headers, your project's headers. Separate each non-empty group with one blank line.

**IMPORTANT:** If a source or header file refers to a symbol defined elsewhere, the file should directly include a header file which properly intends to provide a declaration or definition of that symbol. It should not include header files for any other reason. **Do not rely on transitive inclusions.**

## Namespaces
With few exceptions, place code in a namespace. Namespaces should have unique names based on the project name, and possibly its path. Do not use using-directives (e.g., `using namespace foo`). 
- You may not use a using-directive to make all names from a namespace available.
```cpp
// FORBIDDEN -- This pollutes the namespace.
using namespace foo;
```

## Variables
### Local Variables
Place a function's variables in the narrowest scope possible.
- Initialize variables in the declaration.
```cpp
int i;
i = f();      // BAD -- initialization separate from declaration.
int i = f();  // GOOD -- declaration has initialization.
```
- Prefer initializing using brace initialization.
```cpp
std::vector<int> v; // BAD -- Prefer initializing using brace initialization.
v.push_back(1);  
v.push_back(2);
std::vector<int> v = {1, 2};  // GOOD -- v starts initialized.
```
- Variables needed for `if`, `while` and `for` statements should normally be declared within those statements
```cpp
while (const auto p = text.find('/', str)) {
  str = p + 1;
}
```
- There is **one caveat**: if the variable is an object, its constructor is invoked every time it enters scope and is created, and its destructor is invoked every time it goes out of scope.
```cpp
// INEFFICIENT implementation:
for (int i = 0; i < 1000000; ++i) {
  std::vector<double> vector(10);  // ctor and dtor get called 1000000 times each.
  for(int j = 0; j < 10; ++j) {
    vector[j] = //...
  }
  // do stuff with vector
}

// BETTER implementation:
std::vector<double> vector(10);
for (int i = 0; i < 1000000; ++i) {
  for(int j = 0; j < 10; ++j) {
    vector[j] = //...
  }
  // do stuff with vector
}
```
### Global Variables
Objects with static storage duration are forbidden unless they are trivially destructible.
Note that fundamental types and variables marked with `constexpr` are trivially destructible.
```cpp
const int k_num = 10;  // Allowed

struct X { int n; };
const X k_x[] = {{1}, {2}, {3}};  // Allowed

void foo() {
  static const char* const k_messages[] = {"hello", "world"};  // Allowed
}

constexpr std::array<int, 3> k_array = {1, 2, 3}; // Allowed

// BAD: non-trivial destructor
const std::string k_foo = "foo";

void bar() {
  // BAD: non-trivial destructor.
  static std::map<int, int> k_data = {{1, 0}, {2, 0}, {3, 0}};
}
```
#### Common patterns
- Global strings: if you require a named global or static string constant, consider using a `constexpr` variable of `std::string_view` or character array `char k_str[]`.
- Maps, sets, and other dynamic containers: if you require a static, fixed collection, such as a set to search against or a lookup table, you **cannot use** the dynamic containers from the standard library as a static variable, since they have non-trivial destructors. Instead, consider a simple array of trivial types, e.g., an array of arrays of ints (for a "map from int to int")

## Classes
Classes are the fundamental unit of code in C++. Naturally, we use them extensively.
- Make classes' data members `private`, unless they are constants.
- A class definition should usually start with a `public:` section, followed by `protected:`, then `private:`. Omit sections that would be empty.
- Within each section, prefer grouping similar kinds of declarations together, and prefer the following order:
  -  Types and type aliases (typedef, using, enum, nested structs and classes, and friend types)
  -  (Optionally, for structs only) non-static data members
  -  Static constants
  -  Factory functions
  -  Constructors and assignment operators
  -  Destructor
  -  All other functions (static and non-static member functions, and friend functions)
  -  All other data members (static and non-static)
- Do not define implicit conversions. Use the explicit keyword for conversion operators.


### Struct
- Use a `struct` only for passive objects that carry data; everything else is a `class`.
- Prefer to use a `struct` instead of a pair or a tuple whenever the elements can have meaningful names. **Caveat:** prefer a tuple if you heavily rely on comparing and swapping elements in a list (see [C++ Tuple vs Struct](https://stackoverflow.com/questions/5852261/c-tuple-vs-struct)). 

### Inheritance
- Composition is often more appropriate than inheritance. When using inheritance, make it public. Try to restrict use of inheritance to the "is-a" case.
- Avoid virtual method calls in constructors.
- Explicitly annotate overrides of virtual functions or virtual destructors with exactly one of an `override` or (less frequently) `final` specifier. Do not use `virtual` when declaring an override. Rationale: A function or destructor marked `override` or `final` that is not an override of a base class virtual function will not compile, and this helps catch common errors. 
- Polymorphism is powerful but expensive. Use polymorphism only if you are exploiting the run-time features it provides.

### Operator Overloading
- Overload operators judiciously. Define overloaded operators only if their meaning is obvious, unsurprising, and consistent with the corresponding built-in operators. 
- Define operators only on your own types. More precisely, define them in the same headers, `.cpp` files, and namespaces as the types they operate on. 
- Prefer to define non-modifying binary operators as non-member functions. If a binary operator is defined as a class member, implicit conversions will apply to the right-hand argument, but not the left-hand one. It will confuse your users if a + b compiles but b + a doesn't.
- Do not overload `&&`, `||`, `,` (comma), or unary `&`. Do not overload `operator""`, i.e., do not introduce user-defined literals.
- Don't go out of your way to avoid defining operator overloads. For example, prefer to define `==`, `=`, and `<<`, rather than `Equals()`, `CopyFrom()`, and `PrintTo()`.
- See [cppreference](https://en.cppreference.com/w/cpp/language/operators) for more details

### Friends
We allow use of friend classes and functions, within reason. Friends should usually be defined in the same file so that the reader does not have to look in another file to find uses of the private members of a class. A common use of `friend` is to have a `FooBuilder` class be a friend of Foo so that it can construct the inner state of Foo correctly, without exposing this state to the world. In some cases it may be useful to make a unittest class a friend of the class it tests.


## Functions
Even if C++ is Object-Oriented, do not be afraid of using free functions.
- Parameters are either *inputs* to the function, *outputs* from the function, or *both*.   
    - Non-optional input parameters should usually be values or const references
    - Non-optional output and input/output parameters should usually be references
- When ordering function parameters, put all input-only parameters before any output parameters. 
- Avoid defining functions that require a `const` reference parameter to outlive the call, because `const` reference parameters bind to temporaries. 
- Prefer using return values over output parameters: they improve readability, and often provide the same or better performance (see [RVO](https://en.cppreference.com/w/cpp/language/copy_elision)).
- Prefer placing functions in a namespace. Use completely global functions rarely. 
- **Do not** use a class simply to group static members. Static methods of a class should generally be closely related to instances of the class or the class's static data.
- Define functions `inline` only when they are small, say, 10 lines or fewer.
- Prefer small and focused functions. If a function exceeds about 40 lines, think about whether it can be broken up without harming the structure of the program.
- Use trailing return types only where using the ordinary syntax (leading return types) is impractical or much less readable.
```cpp
auto foo(int x) -> int; // BAD: ordinary syntax is clear
template <typename T, typename U>     // ALLOWED: ordinary syntax is much more verbose
auto add(T t, U u) -> decltype(t + u);
```

## Exceptions
We do not use C++ exceptions. It pollutes the control flow.

## Casting
Use C++-style casts like `static_cast<float>(double_value)`, or brace initialization for conversion of arithmetic types like `int64_t y = int64_t{1} << 42`. Do not use cast formats like `(int)x` unless the cast is to `void`. You may use cast formats like `T(x)` only when `T` is a class type.

## Integer Types
It is often difficult to choose among the many built-in C++ integer types. Keep in mind that implicit casting from one type to another is **expensive**.
- When working with std containers use `size_t` for all the indexes
- If a program needs an integer type of a different size, use an exact-width integer type from `<cstdint>`, such as `int16_t`.
- Try as much as possible not to mix signedness

## Macros
**Avoid as much as possible defining macros**, especially in headers; prefer `inline` functions, `enums`, and `constexpr` variables. 

## Naming conventions

### Types
- Classes, aliases of aggregate types and enums should use `PascalCase`.
- Aliases of fundamental types should use `snake_case` with a trailing `_t`.
- Functions and methods should use `camelCase` (TODO: evaluate this choice)
- Everything else should use `snake_case`.

Examples:
```cpp
class MyClass {
  ...
};
enum class Foo { Bar, Baz };
using VecD = std::vector<double>;
using real_t = float;
```

### Variable prefixes
- Private class attributes should have a prefix `m_`
- Static class attributes should have a prefix `s_`
- `constexpr` and `const` integral variables should have a prefix `k_`

## Control structures
Always brace controlled statements, even a single-line consequent of `if` or `for`.
Examples:
```cpp
if (...) {
} else if (...) {
} else {
}

while (...) {
}

do {
} while (...);

for (...; ...; ...) {
}
```
### Switch
- If an `if else` has more than one branch think to use a `switch`
- If not conditional on an enumerated value, `switch` statements should always have a default case

## Pointers
- Prefer to have single, fixed owners for dynamically allocated objects. Prefer to transfer ownership with smart pointers. That is do not use the keyword `new`, 
- Use `nullptr` for pointers and **not** `NULL` or `0`
- When testing a pointer, use `(!my_ptr)` or `(my_ptr)`; don’t use `my_ptr != nullptr` or `my_ptr == nullptr`.
- Do not compare `x == true` or `x == false`. Use `(x)` or `(!x)`

## Return from errors immediately

In most cases, your knee-jerk reaction should be to return from the current function. Don’t do this:
```cpp
rv = foo->call1();
if (rv) {
  rv = foo->call2();
}
return rv;
```
Instead, do this:
```cpp
rv = foo->call1();
if (!rv) {
  return rv;
}
rv = foo->call2();
return rv;
```