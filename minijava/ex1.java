class Factorial{
    public static void main(String[] a){
        System.out.println(new Fac1().ComputeFac(10));
    }
}

class Fac1 {
    int num_aux1;
    public int ComputeFac(int num){
        if (num < 1)
            num_aux1 = 2 + 8;
        else
            num_aux1 = num * (this.ComputeFac(num-1));
        return num_aux1;
    }
}

class Fac2 {
    int num_aux2;
    public int ComputeFac(int num){
        if (num < 1)
            num_aux2 = 2 + 8;
        else
            num_aux2 = num * (this.ComputeFac(num-1));
        return num_aux2 ;
    }
}


