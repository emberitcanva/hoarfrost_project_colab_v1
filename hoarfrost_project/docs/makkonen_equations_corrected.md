# Corrected Makkonen equations (1)–(15)

Source: Lasse Makkonen, *A model of hoarfrost formation on a cable* (2013).

## Equations

(1)
I = 0.62 \* h \* (e\_s - e\_a) / (c\_p \* p\_a)

(2)
q\_e + q\_s + q\_i = q\_c + q\_eff

(3)
q\_e = L\_e \* I

(4)
q\_c = h \* (T\_s - T\_a)

(5)
h = k\_a \* Nu / D

(6)
Nu\_v = 0.395 \* Gr^0.25

(7)
Gr = g \* D^3 \* |T\_s - T\_a| / (T\_a \* nu^2)

(8)
Nu\_b = a \* Re^0.85

Auxiliary:
Re = v \* D / nu

(9)
q\_eff,0 = sigma \* ( T\_s^4 - (T\_a^4) \* (0.58 + 0.044 \* sqrt(e\_a)) )

(10)
q\_eff = (1 - 0.08 \* n) \* q\_eff,0

(11)
q\_i = (Q\_J + Q\_t) / (pi \* D)

(12)
T\_c = T\_s + (D \* q\_i / (2 \* k\_i)) \* ln(D / d)

(13)
k\_i = 0.0242 + 0.0002 \* rho\_t + 2.54e-6 \* rho\_t^2

(14)
Q\_t = (pi \* d^2 / 4) \* rho\_c \* c\_c \* (Delta\_T\_c / Delta\_tau)

(15)
rho = 650 \* exp(0.227 \* t\_s)

## Notes

* In (4), the correct sign order from the scan is (T\_s - T\_a).
* In (9), e\_a appears under the square root.
* In (12), D appears both as a multiplier of q\_i and inside ln(D/d).
* In (15), exp(0.227 \* t\_s) is the exponential function, not a multiplier.

