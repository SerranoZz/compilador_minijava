class Factorial{
    public static void main(String[] a){
        System.out.println(new Fac1().ComputeFac(10));
    }
}

class Fac1 {
    int num_aux1;
    int num_aux2;
    public int ComputeFac(int num){
        num_aux1 = 5;
        num_aux2 = 3 * num_aux1;
        num_aux1 = num * 2;
        if (num_aux2 < 10)
            num_aux1 = 2 + 8;
        else
            num_aux1 = 5;
        return num_aux1;
    }
}
