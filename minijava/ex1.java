class Factorial{
    public static void main(String[] a){
        System.out.println(new Fac1().ComputeFac11(10, 10, true));
    }
}

class Fac1 {
    int alo1;
    public int ComputeFac11(int num11, int num12, boolean exit){
        int num_aux11;
    	num_aux11 = num11 * (this.ComputeFac11(5, 10, false));
        return num_aux11;
    }

    public int ComputeFac12(int num12, int num2){
        int num_aux12;
    	alo1 = num12 * (this.ComputeFac12(2-2, num_aux12-4));
        return num_aux12;
    }
}
