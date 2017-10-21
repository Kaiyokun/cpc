/*
    !!! ATTENTION !!!
    If you can't read any chinese characters in this file, please select the
    #UTF-8# encoding in your text editor's #Preferences#.

    !!! 注意 !!!
    不要删除原始代码中的任何部分, 只需添加代码即可

    练习内容:
      判断素数. 对于输入n, 如果为素数则返回true, 否则返回false
 */
#include <stdbool.h>

bool IsPrime(int n) {
/************************** TODO: 在下方完成代码功能 **************************/

return false;

/******************************************************************************/

}


#ifndef AUTO_CHECK /* Ignore this line. */


/******************** TODO: #include以及main函数内容可修改 ********************/

#include <stdio.h>

int main(void)
{
    int n;

    printf("Please input a integer number: ");
    scanf("%d", &n);

    printf("Your input: %d\n", n);
    printf("Your output: ");
    if (IsPrime(n))
    {
        printf("%d is a prime number.\n", n);
    }
    else
    {
        printf("%d is not a prime number.\n", n);
    }

    printf("Is that correct? If true, please commit your code; "
        "check your code otherwise.\n");
}

/******************************************************************************/


#endif /* Ignore this line. */
