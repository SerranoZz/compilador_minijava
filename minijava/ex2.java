class Factorial{
    public static void main(String[] a){
        System.out.println(new Fac1().ComputeFac(10));
    }
}

class Fac1 {
    int num_aux1;
    int result;
    public int Sub(int a, int b){
        return a - b;
    }
    
    public int ComputeFac(int num){
        result = this.Sub(2, 1);
        if (num < 1)
            num_aux1 = 2 + 8;
        else
            num_aux1 = num * (this.ComputeFac(num-1));
        return num_aux1;
    }


}

