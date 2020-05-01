# Mapbox Creation

## Hydrography

### Flowlines

Mapbox uses a variation of open street map data to represent water bodies and riverine systems. In order to show lines that coincide with the snapped dams, we removed the 'waterway' dataset from mapbox and instead loaded the NHD Flowlines directly into Mapbox via their API.

### Waterbodies

The same issue of incorrect data exists for waterbodies. Waterbody / ocean data is messier in mapbox - it's drawn over the land, and so you can't simply discard it as then you have no land delineations. Two approaches were available to us:

1. Remove the the 'water' dataset entirely from mapbox, replace the 'land' dataset with a polygonal dataset which accurately represents the region, draw the 'ocean' layer as the background under the new land layer and add waterbodies on top of that.
2. Simply add the waterbodies, knowing the original incorrect data still exists but is mostly in the correct spot - so waterbodies will become on average larger, but there won't be any dramatic issues.

We chose the second option due to time - sourcing an accurate polygon of RI / MA / CT is often difficult, and would require some editing of data that is beyond the scope of this project. The feature types retained were 'LakePond', 'Reservoir' and 'Estuary.'

### Watersheds

We added HUC8, HUC10 and HUC12 polygons to mapbox in order to allow visualization by watershed. These are off by default but can be turned on / swapped between HUC specificity from the client-side JS UI. Additionally, we loaded each dam's watershed into mapbox. This is off by default, but can be toggled to 'show dam watershed on hover or click.'

In total, the follow hydrography datasets were loaded into Mapbox:

- NHD Flowlines for HUC 0109
- NHD Waterbodies for HUC 0109
- HUC8, HUC10 and HUC12 inside region HUC0109.
- Delineated watersheds for each dam.

## Dams

Some datasets are pulled in from the wordpress server. These include:

## UI

## Creating GeoJSON data

## Creating Tilesets fro

If you don't care about the level of zoom on your dataset, you can simply drag
and drop it in the Mapbox "Tilesets" tool to upload the data. This was our initial
approach but we found that all the hydrography data disappeared at high levels
of zoom, which is not a useful thing for a dam atlas to do.

Mapbox allows you to specify the zoom levels, but _only_ if you upload data
through their API, _not_ if you drag and drop. Broadly, here are the notes to do
this and then edit the data.

1. Install their python module, `mapbox-tilesets`. It needs Python >= 3.6. The
    details are available here: [https://github.com/mapbox/tilesets-cli/blob/master/README.md].

    Ideally, you should do this in your dam conda environment, from the python
    command line:

    ```bash
    pip install mapbox-tilesets
    ```

    This python module is a wrapper for their REST API, so you can always use
    the rest API directly - but Mapbox requires newline delimited GeoJSON files
    which are just another hurdle when using the REST API. The python module
    will convert them for you so you don't have to think about it.

    It's useful to look at the API endpoint for the thing you're trying to do,
    and [the entire API can be viewed here.][2]

2. Create a Mapbox secret key for your account. Navigating to the account homepage
    at [https://account.mapbox.com/], scroll down to **Access Tokens**. Create a new
    token that has full access, i.e. check all the boxes and then copy it - you only
    see it once.

3. Export your feature classes to GeoJSON per above.

4. In the python command line, navigate to where you've stored your GeoJSON files.

5. First, you must add your sources to Mapbox - these are the GeoJSON files from
    which your tileset will be created. As a good first step, validate each
    GeoJSON file with:

    ```bash
    > tilesets validate-source file1.json
    ```

    If all is well, you'll see "Validating Features" and then "Valid."

6. Once validated, you can add your source from the GeoJSON files:

    ```bash
    > tilesets add-source <username> <id> <file> --token <your_secret_token>
    ```

    where `username` is your account username, `id` is a new id that you're
    creating and `file` is the GeoJSON file. You can also [also add multiple files and directories.][1]

    The `id` is limited to 32 characters. The only allowed special characters are - and _.

    A tileset source can be a maximum of 10 files or 50 gigabytes.

    A full example of such a command would be:

    ```bash
    > tilesets add-source jsawyeruri wbdhu10 wbdhu10.geojson --token sk.ey3t2bkj23hkhwefkwdf98983...
    ```

7. Once your sources exist, you can now create a tileset. A tileset requires a
    'recipe', i.e. a JSON object which describes the makeup of the tileset. This
    recipe is the reason we're going through this whole process to begin with,
    because here's where you can set the zoom extent of your tileset, a feature
    that's not in the Mapbox drag-and-drop UI. You can have multiple sources in
    your recipe, and each can have their own zoom  levels. An example of
    how this is useful:

    - You can upload a distinct source for each NHD HUC 04 flowline, then composite
        them together in the tileset for a seamless vector dataset.

    - You can upload multiple HUC sizes, e.g. 8, 10 and 12, collect them in one
        tileset and then control which level is shown based on zoom depth.

    A really simple example of a recipe is:

    ```json
    {
        "version": 1,
        "layers": {
            "trees": {
            "source": "mapbox://tileset-source/{username}/trees-data",
            "minzoom": 4,
            "maxzoom": 8
            }
        }
    }
    ```

    ...but if you're going to write recipes and work in this fashion,
    you must [read the References document][3]. Once your recipe is written, you
    create it with the following command:

    ```bash
    tilesets create <tileset_id> --recipe /path/to/recipe.json --name "My neat tileset"
    ```

    where `tileset_id` is something you choose and is composed of your username
    and a 32 character string, e.g. `jsawyeruri.cooltileset_01`.

8. Finally, you can publish your tileset to make it available for use:

    ```bash
    > tilesets publish <tileset_id> --token  <your_secret_token>
    ```

9. It can now be added in Mapbox studio, or added dynamically with javascript.

[1]: (https://github.com/mapbox/tilesets-cli/blob/master/README.md#add-source)
[2]: (https://docs.mapbox.com/api/maps/#tilesets)
[3]: (https://docs.mapbox.com/help/troubleshooting/tileset-recipe-reference/)