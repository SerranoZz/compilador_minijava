class Factorial{
    public static void main(String[] a){
        System.out.println(new Fac2().ComputeFac(10));
    }
}

class Fac {
    int num_aux1;
    public int ComputeFac(int num){
        int num_aux1;
        if (num < 1)
            num_aux2 = 2 + 8;
        else
            num_aux1 = num * (this.ComputeFac(num-1, 7));
        return num_aux1;
    }

    public int ComputeFac(int num){
        num_aux1 = num * (this.ComputeFac(56));
        return num_aux1;
    }
    
}

class Fac1 {
    int num_aux1;
    public int ComputeFac(int num){
        num_aux1 = num * (this.ComputeFac(true));
        return num_aux1;
    }
}

