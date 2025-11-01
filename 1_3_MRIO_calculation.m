
% the code is designed to trace how biodiversity threats propagate through the global economic supply chains
% it connects species-level threat data with the global multi-regional input–output model
% it produces a comprehensive map of how human economic activities contribute to biodiversity threats along international supply chains.

Z = Z_pre2010; % Z: intermediate input matrix
X = X_pre2010; % X: total output 
Y = y_pre2010; % Y: final demand 
% They represent the pre-2010 economic structure.

A = Z ./ X'; % Calculate the technical coefficient matrix A
I = eye(size(A));
L = inv(I - A);% Calculate the Leontief inverse matrix (I - A)^(-1), capturing total (direct + indirect) interdependencies across sectors.

LY_pre2010 = L * Y;   % Total output implied by the input–output model

% Initialize
results = struct();

% Parameters        
block_size   = 26;                         % sectors per country
country_size = 189;                        % number of countries
batch_size   = 100;

df_bio       = df_post2010_io_bio;
unique_types = unique(df_bio.TYPE);

dim = block_size * country_size;           % matrix dimension

%% Loop over species and types
for k = 1:numel(unique_types)
    current_type = unique_types{k};
    fprintf('\nProcessing type: %s (%d/%d)\n', current_type, k, numel(unique_types));

    % Filter rows
    df_current = df_bio(strcmp(df_bio.TYPE, current_type), :);
    n = height(df_current);
    if n == 0
        fprintf('No data for %s\n', current_type);
        continue;
    end

    % Accumulator
    result_bff_total = zeros(dim, dim);

    % Batched aggregation 
    num_batches = ceil(n / batch_size);
    for b = 1:num_batches
        i_start = (b-1)*batch_size + 1;
        i_end   = min(b*batch_size, n);
        m       = i_end - i_start + 1;

        % Build V_batch
        V_batch = zeros(dim, m);
        for jj = 1:m
            i = i_start + jj - 1;
            V_batch(df_current.new_col_io{i}, jj) = df_current.new_val_io{i};
        end

        % Aggregate
        s = sum(V_batch, 2);
        result_bff_total = result_bff_total + (s .* LY_pre2010);
    end

    % Save matrix
    results.(['acc_bf_', current_type]) = result_bff_total;

    fprintf('Finished type %s\n', current_type);
end