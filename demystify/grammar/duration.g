parser grammar duration;

// TODO add more duration
duration : UNTIL duration_end_event
         | FOR AS LONG AS duration_span
         ;

duration_end_event : END OF TURN
                   | SELF LEAVE THE BATTLEFIELD
                   ;

duration_span : ref_object REMAIN EXILED
              ;
