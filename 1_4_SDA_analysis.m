%% === Input data: Z (intermediate flows) and X (total output) for two periods ===

reg_num = 186;
s_num = 26;

% Two time periods
Z0 = Z_pre2010;       % Intermediate input matrix, pre-2010
Z1 = Z_post2010;      % Intermediate input matrix, post-2010

X0 = X_pre2010;       % Total output by sector-region, pre-2010
X1 = X_post2010;      % Total output by sector-region, post-2010

Y0 = FD_pre2010;      % Final demand, pre-2010
Y1 = FD_post2010;     % Final demand, post-2010

% Aggregate final demand to country level 
sum_mat_y = zeros(reg_num * 6, reg_num);
for r = 1:reg_num
    sum_mat_y((r-1)*6 + (1:6), r) = 1;
end
Y0_reg = Y0 * sum_mat_y;
Y1_reg = Y1 * sum_mat_y;

% Environmental extensions (from SDA_Bio)
F0 = pre2010_bio;     % Threatened species intensity coefficients, pre-2010
F1 = post2010_bio;    % Threatened species intensity coefficients, post-2010

% Population data
P0 = table_pop{:, 2}; % Population, pre-2010
P1 = table_pop{:, 3}; % Population, post-2010

% Per-capita final demand matrices (country-sector level)
S0 = Y0_reg ./ P0';   % Final demand per capita, pre-2010
S1 = Y1_reg ./ P1';   % Final demand per capita, post-2010

%% === Compute technical coefficients A and Leontief inverse L ===
A0 = Z0 ./ X0';
A1 = Z1 ./ X1';

% Replace NaN and Inf with zero (numerical cleaning)
A0(isnan(A0)) = 0;
A0(isinf(A0)) = 0;
A1(isnan(A1)) = 0;
A1(isinf(A1)) = 0;

n = size(A0);
I = eye(n);
L0 = inv(I - A0);
L1 = inv(I - A1);

% Clean possible numerical issues in Leontief inverses
L0(isnan(L0)) = 0;
L0(isinf(L0)) = 0;
L1(isnan(L1)) = 0;
L1(isinf(L1)) = 0;

%% === Compute environmental outcome T = F * L * Y ===

T0 = F0 * L0 * (S0 .* P0');   % Threatened species embodied in trade, pre-2010
T1 = F1 * L1 * (S1 .* P1');   % Threatened species embodied in trade, post-2010
deltaT = T1 - T0;

% Changes in drivers between pre- and post-2010
deltaF = F1 - F0; 
deltaL = L1 - L0;
deltaS = S1 - S0;
deltaP = P1 - P0;

% Four-factor full decomposition:
% F = threatened species intensity (environmental coefficients)
% L = production structure / technology (Leontief inverse)
% S = per-capita final demand (consumption level and structure)
% P = population (scale of final demand)
% Using the 1/24 "average of polar decompositions" scheme

E_F = (1/24) * ( ...
      6 * deltaF * L1 * (S1 .* P1') + ...
      2 * deltaF * L1 * (S1 .* P0') + ...
      2 * deltaF * L1 * (S0 .* P1') + ...
      2 * deltaF * L0 * (S1 .* P1') + ...
      2 * deltaF * L1 * (S0 .* P0') + ...
      2 * deltaF * L0 * (S1 .* P0') + ...
      2 * deltaF * L0 * (S0 .* P1') + ...
      6 * deltaF * L0 * (S0 .* P0') );

E_L = (1/24) * ( ...
      6 * F1 * deltaL * (S1 .* P1') + ...
      2 * F1 * deltaL * (S1 .* P0') + ...
      2 * F1 * deltaL * (S0 .* P1') + ...
      2 * F0 * deltaL * (S1 .* P1') + ...
      2 * F1 * deltaL * (S0 .* P0') + ...
      2 * F0 * deltaL * (S1 .* P0') + ...
      2 * F0 * deltaL * (S0 .* P1') + ...
      6 * F0 * deltaL * (S0 .* P0') );

E_S = (1/24) * ( ...
      6 * F1 * L1 * (deltaS .* P1') + ...
      2 * F1 * L1 * (deltaS .* P0') + ...
      2 * F1 * L0 * (deltaS .* P1') + ...
      2 * F0 * L1 * (deltaS .* P1') + ...
      2 * F1 * L0 * (deltaS .* P0') + ...
      2 * F0 * L1 * (deltaS .* P0') + ...
      2 * F0 * L0 * (deltaS .* P1') + ...
      6 * F0 * L0 * (deltaS .* P0') );

E_P = (1/24) * ( ...
      6 * F1 * L1 * ( S1 .* deltaP') + ...
      2 * F1 * L1 * ( S0 .* deltaP') + ...
      2 * F1 * L0 * ( S1 .* deltaP') + ...
      2 * F0 * L1 * ( S1 .* deltaP') + ...
      2 * F1 * L0 * ( S0 .* deltaP') + ...
      2 * F0 * L1 * ( S0 .* deltaP') + ...
      2 * F0 * L0 * ( S1 .* deltaP') + ...
      6 * F0 * L0 * ( S0 .* deltaP') );

E_total = E_F + E_L + E_P + E_S;

% Stack baseline, decomposition terms, and final impacts for export / inspection
% Rows: [T0; E_F; E_L; E_P; E_S; T1], columns: country-sector combinations
E_table = [T0; E_F; E_L; E_P; E_S; T1]';

%% === Check decomposition for a single country (index m) ===
m = 40; % Select a country 

contribF = sum(E_F(m));
contribL = sum(E_L(m));
contribP = sum(E_P(m));
contribS = sum(E_S(m));
contriAll = sum(E_total(m));

Error = contriAll - contribF - contribL - contribP - contribS;

fprintf('\n=== Full decomposition (E = F·L·Y), single country m = %d ===\n', m);
fprintf('E0 (total)                 : %.6f\n', sum(T0(m)));
fprintf('E1 (total)                 : %.6f\n', sum(T1(m)));
fprintf('ΔE total                   : %.6f\n', contriAll);
fprintf('  ΔE_F (Intensity, F)      : %.6f\n', contribF);
fprintf('  ΔE_L (Structure, L)      : %.6f\n', contribL);
fprintf('  ΔE_P (Population, P)     : %.6f\n', contribP);
fprintf('  ΔE_S (Per-capita FD, S)  : %.6f\n', contribS);
fprintf('Closure error              : %.3e\n', Error);

%% === Check decomposition for all countries (global total) ===

contribF = sum(E_F, 'all');
contribL = sum(E_L, 'all');
contribP = sum(E_P, 'all');
contribS = sum(E_S, 'all');
contriAll = sum(E_total, 'all');

Error = contriAll - contribF - contribL - contribP - contribS;

fprintf('\n=== Full decomposition (E = F·L·Y), global total ===\n');
fprintf('E0 (total)                 : %.6f\n', sum(T0, 'all'));
fprintf('E1 (total)                 : %.6f\n', sum(T1, 'all'));
fprintf('ΔE total                   : %.6f\n', contriAll);
fprintf('  ΔE_F (Intensity, F)      : %.6f\n', contribF);
fprintf('  ΔE_L (Structure, L)      : %.6f\n', contribL);
fprintf('  ΔE_P (Population, P)     : %.6f\n', contribP);
fprintf('  ΔE_S (Per-capita FD, S)  : %.6f\n', contribS);
fprintf('Closure error              : %.3e\n', Error);
