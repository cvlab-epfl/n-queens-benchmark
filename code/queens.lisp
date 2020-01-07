;;-------------------------------------------------------------
;;                     USE  RECURSION
;;=============================================================

(defun allQueensAux(n i col dg1 dg2)
  ;; Optional declarations. Some compilers exploit them to speed up the code
  ;(declare (type (array boolean 1) col dg1 dg2 ))
  (declare (type fixnum n i))

  (if (= i n)
      
      1

    (let ((nsol 0))
       (declare (type fixnum nsol))
    
      (loop for j from 0 below n 
	    when (and (aref col j) (aref dg1 (+ i j)) (aref dg2 (- (+ i n) j)))
	    do
              
              (setf 
                (aref col j) nil
                (aref dg1 (+ i j)) nil
                (aref dg2 (- (+ i n) j)) nil)
              
              (incf nsol (allQueensAux n (+ i 1) col dg1 dg2))
              
              (setf
	        (aref col j) t
                (aref dg1 (+ i j)) t
                (aref dg2 (- (+ i n) j)) t))
      (the fixnum nsol))))

(defun allQueensRec(n)
  (declare (type fixnum n))

  (let ((col (make-array n       :initial-element t :element-type 'boolean))
        (dg1 (make-array (* 2 n) :initial-element t :element-type 'boolean))
        (dg2 (make-array (* 2 n) :initial-element t :element-type 'boolean)))
    (declare (type (array boolean 1) col dg1 dg2 ))
    
    (allQueensAux n 0 col dg1 dg2)))

(defun test-queens (fromN toN rept)
  (format t "Benchmark queens~%")
  (loop with np = rept and dt
      for n from fromN to toN
      for t0 = (get-internal-real-time)
      do(loop repeat np do (allQueensRec n))
        (setq dt (/ (-(get-internal-real-time) t0) (* rept internal-time-units-per-second)))
        (format t "~2d: ~f~%" n dt)))


(compile `allQueensAux)
(compile `allQueensRec)
(compile `test-queens)
(test-queens 8 14 10)
	      

;(cd "/Users/fua/code/acl")
;(compile-file "/Users/fua/code/acl/queens.lisp”)
;(allQueensRec 8)




