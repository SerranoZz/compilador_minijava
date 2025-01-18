class Factorial{
    public static void main(String[] a){
        System.out.println(new Fac().ComputeFac(10));
    }
}

class Fac {
    int num_aux1;
    public int ComputeFac(int num){
        int num_aux2;
        if (num < 1)
            num_aux1 = 2 + 8;
        else
            num_aux1 = num * (this.ComputeFac(num-1));
        return num_aux1;
    }
}
