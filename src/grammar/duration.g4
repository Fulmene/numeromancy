parser grammar duration;

// TODO add more duration
duration : UNTIL durationEnd
         | FOR AS LONG AS durationSpan
         ;

durationEnd : END OF TURN
            | refObject LEAVE THE BATTLEFIELD
            ;

durationSpan : refObject REMAIN EXILED
             | refPlayer CONTROL refObject
             ;
