# What's this?
- Some royalty free musics that you can add directly to your favorite BN soundpack
- `musicset.json` contains all the musics path that bright night will play randomly during gameplay
- Next to `soundpack.txt` (in `your_soundpack_path/(...)/`) create a folder named `music` if it doesn't exist already
# Case 1 - I don't have a musicset.json file in my soundpack
- Add everything here in your new `music` folder and you're done -> in that case we're adding musics to a soundpack that didn't have any (eg: https://github.com/nheve/Otopack-Revived-BN/tree/master/Otopack%2BModsUpdates) 
# Case 2 - I have a musicset.json file in my soundpack
- Drag & Drop the musics folder(s) (`WBC`, ...) in the `music` folder
## Method 1 - Replace all the musics
- Overwrite your `musicset.json` with the one here, you're done
## Method 2 - Add the musics while keeping the others from your soundpack
- Open the `musicset.json` from your soundpack and the one here with a text editor
- In the `musicset.json` of your soundpack, add a `,` after the last closed pointy bracket (the last music line), and copy paste the content inside the square brackets after `"files" :`
![quick_tuto_merging_musics](quick_tuto_merging_musics.png)

# In any case
- Feel free to remove the musics you don't like by removing json lines from `musicset.json`, you can also tweak their volumes here

# Credits
- All the musics in **WBC** *(White Bat Cyberpunk)* are **made by "Karl Casey @ White Bat Audio"** [source](https://www.youtube.com/watch?v=zyNjF_PIvGM) and quoting him
	- "Can I use this in my video/stream/film/game/project/podcast etc.? -> Yes, my music is 100% copyright free so you can use it in ANY creative project, just credit me "music by Karl Casey @ White Bat Audio". What you CANNOT do is take my music and redistribute it as a product."
 - All the musics in **WBJC** _(White Bat John Carpenter)_ are also **made by "Karl Casey @ White Bat Audio"** [source](https://www.youtube.com/watch?v=Eiijm2GhKAA)
 - All the musics in **WBUV** _(White Bat Ultra Violent)_ are also **made by "Karl Casey @ White Bat Audio"** [source](https://youtu.be/VaVmI29rxys)
 - All the musics in **WBHS** _(White Bat Horror Synth)_ are also **made by "Karl Casey @ White Bat Audio"** [source](https://youtu.be/9_KDUsQwLYQ)
