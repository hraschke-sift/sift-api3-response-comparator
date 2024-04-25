#!/bin/bash
#!/bin/bash

osascript -e 'tell application "iTerm2" to activate'

osascript -e 'tell application "iTerm2"
  create window with default profile
  tell current session of current window
    write text "/Users/hraschke/sift/tools/sift-api3-response-comparator/src/cli.py --env=stg1 --config-path=config-1.json"
  end tell
end tell'

osascript -e 'tell application "iTerm2"
  create window with default profile
  tell current session of current window
    write text "/Users/hraschke/sift/tools/sift-api3-response-comparator/src/cli.py --env=stg1 --config-path=config-0.json"
  end tell
end tell'

osascript -e 'tell application "iTerm2"
  create window with default profile
  tell current session of current window
    write text "/Users/hraschke/sift/tools/sift-api3-response-comparator/src/cli.py --env=stg1 --config-path=config-2.json"
  end tell
end tell'

osascript -e 'tell application "iTerm2"
  create window with default profile
  tell current session of current window
    write text "/Users/hraschke/sift/tools/sift-api3-response-comparator/src/cli.py --env=stg1 --config-path=config-3.json"
  end tell
end tell'

osascript -e 'tell application "iTerm2"
  create window with default profile
  tell current session of current window
    write text "/Users/hraschke/sift/tools/sift-api3-response-comparator/src/cli.py --env=stg1 --config-path=config-4.json"
  end tell
end tell'

osascript -e 'tell application "iTerm2"
  create window with default profile
  tell current session of current window
    write text "/Users/hraschke/sift/tools/sift-api3-response-comparator/src/cli.py --env=stg1 --config-path=config-5.json"
  end tell
end tell'

osascript -e 'tell application "iTerm2"
  create window with default profile
  tell current session of current window
    write text "/Users/hraschke/sift/tools/sift-api3-response-comparator/src/cli.py --env=stg1 --config-path=config-6.json"
  end tell
end tell'

osascript -e 'tell application "iTerm2"
  create window with default profile
  tell current session of current window
    write text "/Users/hraschke/sift/tools/sift-api3-response-comparator/src/cli.py --env=stg1 --config-path=config-7.json"
  end tell
end tell'

osascript -e 'tell application "iTerm2"
  create window with default profile
  tell current session of current window
    write text "/Users/hraschke/sift/tools/sift-api3-response-comparator/src/cli.py --env=stg1 --config-path=config-8.json"
  end tell
end tell'
