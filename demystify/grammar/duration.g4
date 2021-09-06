parser grammar duration;

// TODO add more duration
duration : UNTIL durationEndEvent
         | FOR AS LONG AS durationSpan
         ;

durationEndEvent : END OF TURN
                 | SELF LEAVE THE BATTLEFIELD
                 ;

durationSpan : refObject REMAIN EXILED
             ;
