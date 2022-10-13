set title "Absorption spectrum (Lorentzian, FWHM=0.05 eV)\n500 Initial conditions, *"

set xrange [2.00000:5.000000]
set yrange [0.000000:0.005000]
set xlabel "Energy (eV)"
set ylabel "Cross section ({\\305}^2 molecule ^-^1)"

set style fill transparent solid 0.25 border
set term pngcairo enhanced font "Helvetica,26.0" size 1000,800
set out '*.png'
set key left

plot "cross-section_2.dat" u 1:3 w filledcu y1=0 tit "S_1" lw 0.5 lc rgbcolor "#7a0403", \
     "cross-section_3.dat" u 1:3 w filledcu y1=0 tit "S_2" lw 0.5 lc rgbcolor "#fb7e21", \
     "cross-section_4.dat" u 1:3 w filledcu y1=0 tit "S_3" lw 0.5 lc rgbcolor "#a4fc3c", \
     "cross-section_5.dat" u 1:3 w filledcu y1=0 tit "S_4" lw 0.5 lc rgbcolor "#28bceb", \
     "cross-section_all.dat" u 1:3 w l tit "Sum" lw 3.0 lc rgbcolor "black"
