# music-mood-recommender-app

## Table of Contents
1. [Project introduction](#project-introduction)
2. [How does the app work](#how-does-the-app-work)
3. [Project background](#project-background):
    1. [Defining mood of the music](#defining-mood-of-the-music)
    2. [Data collection and data analysis](#data-collection-and-data-analysis)
    3. [Machine learning algorithm selection](#machine-learning-algorithm-selection)
    4. [Music genres definition](#music-genres-definition)
4. [Run app locally](#run-app-locally)
5. [Build docker image](#build-docker-image)

## Project introduction

This project is a part of my bachelor's thesis aimed at developing a web application with a music recommender system.
The system allows users to select their mood (in range of four categories) and a preferred music genre, after which a
playlist of 20 songs is recommended. The system integrates machine learning (ML) techniques to predict probability of
songs belonging to each of the four mood categories.

## How does the app work

First of all, user selects a mood on a 2D slider where **X** and **Y** coordinates take values between 0.0 and 1.0.
Probabilities of each mood category are calculated in the following way:

$$p_{happy} = x * y;$$

$$p_{aggressive} = (1 - x) * y;$$

$$p_{sad} = (1 - x) * (1 - y);$$

$$p_{calm} = x * (1 - y)$$

Which means that when a song belongs to a given mood category with probability of 100% it corresponds to the following *
*X** and **Y** coordinates:

- **Happy**: $x=1; y=1$
- **Aggressive**: $x=0; y=1$
- **Sad**: $x=0; y=0$
- **Calm**: $x=1; y=0$

Then user selects only one preferred genre. After that the query to the database with calculated mood probabilities (
from **X** and **Y** coordinates) and chosen genre id is performed. Then server takes 20 random songs from the query and
returns them to the user.

<p align="center">
  <img src="https://github.com/user-attachments/assets/a2be1d95-9c7b-4e98-bb04-12a27b05ba7c" width="30%" alt="Choose Mood Screen" />
  <img src="https://github.com/user-attachments/assets/397929cd-fc57-4047-bbee-948e8ceff89e" width="30%" alt="Choose Genre Screen" />
  <img src="https://github.com/user-attachments/assets/2427fff8-5421-4c8b-80c2-a2ee770f4e9b" width="30%" alt="Generated Playlist" />
</p>

<p align="center">
  <b>Figure 1:</b> User interface showing (left) mood selection, (middle) genre selection, and (right) generated playlist.
</p>

### Database Schema

#### Song Table

| Column Name       | Data Type   | Constraints                       | Description                                 |
|-------------------|-------------|-----------------------------------|---------------------------------------------|
| `id`              | Integer     | Primary Key                       | Unique identifier for each song             |
| `artist_name`     | String(512) | Not Null                          | Name of the artist                          |
| `album_name`      | String(255) | Not Null                          | Name of the album                           |
| `track_name`      | String(512) | Not Null                          | Name of the track                           |
| `happy`           | Float       | Indexed                           | Probability score for the 'happy' mood      |
| `aggressive`      | Float       | Indexed                           | Probability score for the 'aggressive' mood |
| `sad`             | Float       | Indexed                           | Probability score for the 'sad' mood        |
| `calm`            | Float       | Indexed                           | Probability score for the 'calm' mood       |
| `genre_id`        | Integer     | Foreign Key (references Genre.id) | Identifier linking to the genre of the song |
| `album_cover_url` | String(255) | Nullable                          | URL for the album cover image               |

**Unique Constraint:**

- `uq_artist_album_track`: Ensures a unique combination of `artist_name`, `album_name`, and `track_name`.

---

#### Genre Table

| Column Name | Data Type  | Constraints      | Description                      |
|-------------|------------|------------------|----------------------------------|
| `id`        | Integer    | Primary Key      | Unique identifier for each genre |
| `name`      | String(64) | Not Null, Unique | Name of the genre                |

**Unique Constraint:**

- `uq_genre`: Ensures unique genre names.

---

#### Admin Table

| Column Name     | Data Type   | Constraints      | Description                              |
|-----------------|-------------|------------------|------------------------------------------|
| `id`            | Integer     | Primary Key      | Unique identifier for each admin         |
| `username`      | String(50)  | Not Null, Unique | Username for admin authentication        |
| `password_hash` | String(300) | Not Null         | Hashed password for admin authentication |

**Unique Constraint:**

- `uq_username`: Ensures unique usernames for admins.

## Project background

This section introduces some background on research done in my thesis. It mostly focuses on the task of predicting
probabilities of songs belonging to the chosen mood categories. We decided to predict probabilities instead of class
labels so that user would be able to choose the mood of the music with more variety.

### Defining mood of the music

The mood categories were defined based on the circumplex model of affect
by [Russell (1980)](https://psycnet.apa.org/doi/10.1037/h0077714). This model organizes emotions
along two independent dimensions:

1. Valence (ranging from positive to negative emotions).
2. Arousal (ranging from high-energy to low-energy states).

By mapping valence on the horizontal axis and arousal on the vertical axis, four quadrants emerge, each corresponding to
a specific mood:

- **Happy** (high valence, high energy)
- **Aggressive** (low valence, high energy)
- **Sad** (low valence, low energy)
- **Calm** (high valence, low energy)

Music in this project is classified based on these four mood categories using machine learning. At first we assumed
valence and arousal (obtained
using [Spotify API](https://developer.spotify.com/documentation/web-api/reference/get-audio-features)) would be enough
to classify the songs, but further research has proven otherwise.

### Data collection and data analysis

The dataset was collected by scraping playlists from Spotify. Playlists containing at least 1000 followers and whose
names included mood-related keywords (such as "happy," "sad," etc.) were selected. This ensured that the music in these
playlists was representative of the chosen moods.

For each mood category (happy, aggressive, sad, and calm), we selected 14 keywords from
the [ANEW list (Bradley et al., 1999)](https://pdodds.w3.uvm.edu/teaching/courses/2009-08UVM-300/docs/others/everything/bradley1999a.pdf)
using the logic similar to [Çano et al. (2017)](http://dx.doi.org/10.5121/csit.2017.70603).
Keywords were evaluated for relevance to avoid ambiguous
results (e.g., playlists related to specific artists or soundtracks). Only the top two popular keywords with high
follower counts were chosen per mood quadrant.

Using the [Spotify API](https://developer.spotify.com/documentation/web-api/reference/get-audio-features), key
attributes of each song were extracted, such as valence, energy, tempo, loudness, danceability, etc. The final dataset
comprised **4483** songs, distributed as follows:

- **1149** for the "Happy" mood,
- **1139** for "Aggressive",
- **1105** for "Sad",
- **1090** for "Calm".

To find more details on how data was collected and results of its analysis, please consider reading my article (
published in Russian languge): [PDF link](https://na-journal.ru/pdf/nauchnyi_aspekt_6-2024_t49_web.pdf#page=31).

### Machine learning algorithm selection

To determine the best algorithm for mood prediction, we trained and tested several machine learning classification
models, including:

- [Decision Tree](https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html)
- [Random Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)
- Gradient
  Boosting ([XGBoost](https://xgboost.readthedocs.io/en/stable/), [LightGBM](https://lightgbm.readthedocs.io/en/stable/), [CatBoost](https://catboost.ai/))

After hyperparameter tuning using the Tree-structured Parzen Estimator (TPE) algorithm in
the [Optuna](https://optuna.org/) library and calibrating predicted probabilities
via [sigmoid regressor](https://scikit-learn.org/stable/modules/calibration.html#sigmoid)
and [isotonic regressor](https://scikit-learn.org/stable/modules/calibration.html#isotonic), CatBoost with isotonic
calibration achieved the best results and was further used for predicting probabilities of songs' moods. The performance
was evaluated using [LogLoss](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.log_loss.html),
[AUC-ROC](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html), Brier
Score ([Kruppa et al., 2014](https://doi.org/10.1002/bimj.201300068)) and Expected Calibration
Error ([Guo et al., 2017](https://doi.org/10.48550/arXiv.1706.04599)).

### Music genres definition

To classify the music genres of the songs in our project, we utilized tags from the Last.fm service. Last.fm allows
users to tag artists, albums, and individual tracks. Using the public [Last.fm API](https://www.last.fm/api), we
collected the most popular tags
assigned to tracks. However, since these tags are not always directly related to musical genres, a dictionary-based
filtering method was employed to extract relevant genre information.

For the genre dictionary, we used a genre tree provided by the developers of
the [LastGenre plugin](https://beets.readthedocs.io/en/stable/plugins/lastgenre.html) for the music library
manager [beets](https://beets.io/). This genre tree includes a comprehensive list of 766 genres compiled from Wikipedia
articles about
musical genres. A specialized filtering method, similar to LastGenre's approach, was implemented to map tags to valid
genres.

## Citation
If you find this project helpful and use it in your research, please consider citing our article published among with my thesis:

### Russian (original)
```bibtex
@article{silinskaya2024classification,
  author    = {Иванова, А. С. and Силинская, А. А.},
  title     = {Классификация музыки по настроению с помощью алгоритмов машинного обучения},
  journal   = {Научный аспект},
  year      = {2024},
  volume    = {49},
  number    = {6},
  pages     = {6217--6224},
  note      = {EDN IMYGVB},
  url       = {https://www.elibrary.ru/imygvb}
}
```

### English (transliteration)
```bibtex
@article{silinskaya2024classification,
  author    = {Ivanova, A. S. and Silinskaya, A. A.},
  title     = {Klassifikatsiya muzyki po nastroeniyu s pomoshch'yu algoritmov mashinnogo obucheniya},
  journal   = {Nauchny aspekt},
  year      = {2024},
  volume    = {49},
  number    = {6},
  pages     = {6217--6224},
  note      = {Available at: \url{https://www.elibrary.ru/imygvb} and \url{https://na-journal.ru/pdf/nauchnyi_aspekt_6-2024_t49_web.pdf#page=31}},
  url       = {https://www.elibrary.ru/imygvb}
}
```

Read the original text of the article here (in Russian): [PDF link](https://na-journal.ru/pdf/nauchnyi_aspekt_6-2024_t49_web.pdf#page=31)

## Run app locally

### Prerequisites

Ensure you have the following installed on your machine:

- Python 3.10+
- PostgreSQL
- [Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/)
- Virtualenv

### Installation

#### Clone the Repository

```bash
git clone https://github.com/annsilin/music-mood-recommender-app.git
cd music-mood-recommender-app
```

#### Set Up the Virtual Environment

On Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```cmd
python -m venv venv
.\venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment Variables

Set the necessary environment variables in your OS. On Linux or macOS, you can use `export`:

```bash
export DATABASE_URL=postgresql://username:password@localhost:5432/yourdatabase
export JWT_SECRET_KEY=your-jwt-secret-key
export FLASK_RUN_PORT=5000
export LASTFM_API_KEY=your-lastfm-api-key
export LASTFM_SECRET_KEY=your-lastfm-api-key
```

On Windows, use `set`:

```cmd
set DATABASE_URL=postgresql://username:password@localhost:5432/yourdatabase
set JWT_SECRET_KEY=your-jwt-secret-key
set FLASK_RUN_PORT=5000
set LASTFM_API_KEY=your-lastfm-api-key
set LASTFM_SECRET_KEY=your-lastfm-api-key
```

Replace `username`, `password`, `localhost`, `5432`, and `yourdatabase` with your PostgreSQL credentials and database
name.

`LASTFM_API_KEY` and `LASTFM_SECRET_KEY` are needed in order to use functionality to fetch music genre and/or album
cover using
Last.fm API when adding songs to the database via admin UI. If you don't need this functionality, you can skip adding
these variables, otherwise obtain your credentials from https://www.last.fm/en/api

#### Initialize the Database

Ensure PostgreSQL is running and create your database if it doesn't exist.

Run the following commands to initialize the database:

```bash
flask db init
flask db upgrade
```

### Running the Application

#### Start Redis Server

Ensure the Redis server is running. You can start it using:

```bash
sudo service redis-server start
```

#### Start the Flask Application

```bash
flask run
```

#### Start the RQ Worker

In a separate terminal window, start the RQ worker:

```bash
rq worker
```

#### Adding Admin user

Admin user is needed in order to perform requests from admin UI on `<your_app_url>/admin` page. These requests include
populating database from `.csv` table, monitoring statuses of background jobs and removing background jobs.

Execute Flask CLI command to add admin user into the database:

```bash
flask create_admin <username>
```

If you want to delete admin user from the database, execute this command:

```bash
flask remove_admin <username>
```

#### Populating the database

If you want to populate the database with the songs using admin UI, navigate to `<your_app_url>/admin` in your browser
window, authorize with admin account created with CLI command and follow the on-page instructions.

## Build docker image

To spin up everything, run 'docker-compose' in the root of this project:

```shell
docker-compose up
```

### Create admin

To create an admin one could use the following command:

```shell
docker exec -it music-mood-recommender-app flask create-admin <username>
```
