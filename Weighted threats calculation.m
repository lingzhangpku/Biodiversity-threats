
%% Introduction
% Based on species-specific data across countries (including human footprint and land area)
% Calculate the proportion of human activity intensity and habitat area that each country represents within a species  distribution range.

%% Part1 =========================
% 1. Data Preparation and Cleaning 

% Original dataset
Data_hf = df1_hf_time2;  % Human footprint data

% Initialize CountryID column as zeros (indicating not yet matched)
Data_hf.CountryID = zeros(height(Data_hf), 1);

% Match country names and assign CountryID based on reference list
[tf, loc] = ismember(Data_hf.country, country_ID.shp_country);  % tf: match success; loc: index position
Data_hf.CountryID(tf) = country_ID.IO_id(loc(tf));  % Assign corresponding IO_id for matched rows

% Keep only successfully matched rows (remove unmatched countries)
Data_hf = Data_hf(Data_hf.CountryID ~= 0, :);

% =========================
% 2. Loop through each species

% Get list of unique species names
uniqueNames = unique(Data_hf.sci_name);

% Initialize output columns (for storing nested HF proportions and country IDs)
Data_hf.hf_ave = cell(height(Data_hf), 1);
Data_hf.countriesID = cell(height(Data_hf), 1);

% Iterate through each species
for i = 1:length(uniqueNames)
    currentName = uniqueNames{i};                  % Current species name
    rows = strcmp(Data_hf.sci_name, currentName);  % Select rows belonging to this species

    % Extract country names and IDs
    countries = Data_hf.country(rows);
    countries_ID = num2cell(Data_hf.CountryID(rows));

    % Extract HF data (pre- and post-2010)
    hf_data = Data_hf{rows, {'hf_pre_2010', 'hf_post_2010'}};

    % Compute total HF for both time periods
    total = sum(hf_data, 1);

    % Compute proportions per country (avoid division by zero)
    proportions = zeros(size(hf_data));
    nonzero = total ~= 0;
    proportions(:, nonzero) = hf_data(:, nonzero) ./ total(nonzero);

    % Combine into a nested structure: country, ID, and HF proportions
    nested_hf = [countries, countries_ID, num2cell(proportions)];

    % Store the nested results in the corresponding rows
    Data_hf.hf_ave(rows) = {nested_hf};
    Data_hf.countriesID(rows) = {strjoin(string([Data_hf.CountryID(rows)]'), ',')};
end

% =========================
% 3. Deduplication and Output

% Extract key columns: species name, list of country IDs, and nested HF data
[~, idx] = unique(Data_hf.sci_name, 'stable');
df_hf_nest = Data_hf(idx, {'sci_name', 'countriesID', 'hf_ave'});



%% Part2 =========================
% 1. Data preparation and country matching

% Original dataset
Data_land = df1_land_time2;  % land use data

% Initialize CountryID column with zeros 
Data_land.CountryID = zeros(height(Data_land), 1);

% Match country names with the reference table 'country_ID'
[tf, loc] = ismember(Data_land.country, country_ID.shp_country);

% Assign matched IO_id values to CountryID
Data_land.countryID(tf) = country_ID.IO_id(loc(tf));

% Keep only successfully matched rows (remove where countryID = 0)
Data_land = Data_land(Data_land.countryID ~= 0, :);

% =========================
% 2. Initialization and variable setup

% Get unique species names
uniqueNames = unique(Data_land.sci_name);

% Preallocate memory for nested results (improves efficiency)
Data_land.countries_LA = cell(height(Data_land), 1);       % original land area
Data_land.countries_LA_pro = cell(height(Data_land), 1);   % proportional land area
Data_land.countriesID = cell(height(Data_land), 1);        % list of country IDs

% Extract land area matrix (two columns: pre- and post-2010)
landAreaMatrix = Data_land{:, {'land_pre_2010', 'land_post_2010'}};

% =========================
% 3. Loop over each species

for i = 1:length(uniqueNames)
    % Current species name
    currentName = uniqueNames{i};
    
    % Select all rows belonging to the current species
    rows = strcmp(Data_land.sci_name, currentName);
    
    % Extract country names and corresponding IDs
    countries_LA = Data_land.country(rows);
    countries_ID = num2cell(Data_land.countryID(rows));
    
    % Extract land area values
    landAreaData = landAreaMatrix(rows, :);
    
    % Compute total land area for the species (both years)
    totalArea = sum(landAreaData, 1);
    
    % Compute each country's proportion in total area
    proportions = landAreaData ./ totalArea;
    
    % Combine into nested structures:
    % ① Raw areas: [country, countryID, landAreaData]
    % ② Proportions: [country, countryID, proportional values]
    nestedCountries = [countries_LA, countries_ID, num2cell(landAreaData)];
    nestedCountries_area_pro = [countries_LA, countries_ID, num2cell(proportions)];
    
    % Write nested results back to corresponding rows
    Data_land.countries_LA(rows) = {nestedCountries};
    Data_land.countries_LA_pro(rows) = {nestedCountries_area_pro};
    Data_land.countriesID(rows) = {strjoin(string(countries_ID), ',')};
end

% =========================
% 4. Deduplication and output

% Keep essential columns for output
[~, idx] = unique(Data_land.sci_name, 'stable');
df_land_nest = Data_land(idx, :);
df_land_nest = df_land_nest(:, {'sci_name','countriesID','countries_LA_pro'});

% Display result table
disp(df_land_nest);
