# FIXME: PlotFactory methods plot, geweke_plot, bar_series_plot, gof_plot not working.

"""
Plotting module using matplotlib.
"""

# Import matplotlib functions
import matplotlib
import pymc
import os
from pylab import bar, hist, plot as pyplot, xlabel, ylabel, xlim, ylim, close, savefig, figure, subplot, gca, scatter
from pylab import setp, axis, contourf, cm, title, colorbar, clf, fill, show
from pprint import pformat

# Import numpy functions
from numpy import arange, log, ravel, rank, swapaxes, linspace#, interp
from numpy import arange, log, ravel, rank, swapaxes, concatenate
from numpy import histogram2d, mean, std, sort, prod, floor, shape, transpose
from numpy import apply_along_axis
import pdb

__all__ = ['func_quantiles', 'func_envelopes', 'func_sd_envelope', 'centered_envelope', 'get_index_list', 'plot', 'histogram', 'trace', 'geweke_plot', 'gof_plot', 'bar_series_plot', 'pair_posterior']

def get_index_list(shape, j):
    """
    index_list = get_index_list(shape, j)

    :Arguments:
        shape: a tuple
        j: an integer

    Assumes index j is from a ravelled version of an array
    with specified shape, returns the corresponding
    non-ravelled index tuple as a list.
    """

    r = range(len(shape))
    index_list = (r)

    for i in r:
        if i < len(shape):
            prodshape = prod(shape[i+1:])
        else:
            prodshape=0
        index_list[i] = int(floor(j/prodshape))
        if index_list[i]>shape[i]:
            raise IndexError, 'Requested index too large'
        j %= prodshape

    return index_list

def func_quantiles(node, qlist=[.025, .25, .5, .75, .975]):
    """
    Returns an array whose ith row is the q[i]th quantile of the 
    function.

    :Arguments:
        func_stacks: The samples of the function. func_stacks[i,:] 
            gives sample i.
        qlist: A list or array of the quantiles you would like.

    :SeeAlso: func_envelopes, func_hist, weightplot
    """

    # For very large objects, this will be rather long. 
    # Too get the length of the table, use obj.trace.length()
    
    if isinstance(node, pymc.Variable):
        func_stacks = node.trace()
    else:
        func_stacks = node

    if any(qlist<0.) or any(qlist>1.):
        raise TypeError, 'The elements of qlist must be between 0 and 1'

    func_stacks = func_stacks.copy()

    N_samp = shape(func_stacks)[0]
    func_len = tuple(shape(func_stacks)[1:])

    func_stacks.sort(axis=0)

    quants = zeros((len(qlist),func_len),dtype=float)
    alphas = 1.-abs(array(qlist)-.5)/.5

    for i in range(len(qlist)):
        quants[i,] = func_stacks[int(qlist[i]*N_samp),]

    return quants, alphas

def func_envelopes(node, CI=[.25, .5, .95]):
    """
    func_envelopes(node, CI = [.25, .5, .95])

    Returns a list of centered_envelope objects for func_stacks,
    each one corresponding to an element of CI, and one 
    corresponding to mass 0 (the median).

    :Arguments:
        func_stacks: The samples of the function. func_stacks[i,:] 
            gives sample i.
        CI: A list or array containing the probability masses
            the envelopes should enclose.

    :Note: The return list of envelopes is sorted from high to low
        enclosing probability masses, so they should be plotted in
        order.

    :SeeAlso: centered_envelope, func_quantiles, func_hist, weightplot
    """

    if isinstance(node, pymc.Variable):
        func_stacks = node.trace()
    else:
        func_stacks = node

    func_stacks = func_stacks.copy()
    func_stacks.sort(axis=0)

    envelopes = []
    qsort = sort(CI)

    for i in range(len(qsort)):
        envelopes.append(centered_envelope(func_stacks, qsort[len(qsort)-i-1]))
    envelopes.append(centered_envelope(func_stacks, 0.))

    return envelopes

# FIXME: Not sure of the best way to bring these two into PlotFactory...
class func_sd_envelope(object):
    """
    F = func_sd_envelope(func_stacks)
    F.display(axes,xlab=None,ylab=None,name=None)

    This object plots the mean and +/- 1 sd error bars for 
    the one or two-dimensional function whose trace
    """

    def __init__(self, node, format='pdf', plotpath='', suffix=''):

        if isinstance(node, pymc.Variable):
            func_stacks = node.trace()
        else:
            func_stacks = node
        self.name = node.__name__
        self._format=format
        self._plotpath=plotpath
        self.suffix=suffix

        self.mean = mean(func_stacks,axis=0)
        self.std = std(func_stacks, axis=0)

        self.lo = self.mean - self.std
        self.hi = self.mean + self.std

        self.ndim = len(shape(func_stacks))-1


    def display(self,axes,xlab=None,ylab=None,name=None,new=True):
        if name:
            name_str = name
        else:
            name_str = ''

        if self.ndim==1:
            if new:
                figure()
            pyplot(axes,self.lo,'k-.',label=name_str+' mean-sd')
            pyplot(axes,self.hi,'k-.',label=name_str+'mean+sd')
            pyplot(axes,self.mean,'k-',label=name_str+'mean')
            if name:
                title(name)

        elif self.ndim==2:
            if new:
                figure(figsize=(14,4))
            subplot(1,3,1)
            contourf(axes[0],axes[1],self.lo,cmap=cm.bone)
            title(name_str+' mean-sd')
            if xlab:
                xlabel(xlab)
            if ylab:
                ylabel(ylab)        
            colorbar()

            subplot(1,3,2)
            contourf(axes[0],axes[1],self.mean,cmap=cm.bone)
            title(name_str+' mean')
            if xlab:
                xlabel(xlab)
            if ylab:
                ylabel(ylab)
            colorbar()      

            subplot(1,3,3)
            contourf(axes[0],axes[1],self.hi,cmap=cm.bone)
            title(name_str+' mean+sd')
            if xlab:
                xlabel(xlab)
            if ylab:
                ylabel(ylab)
            colorbar()
        else:
            raise ValueError, 'Only 1- and 2- dimensional functions can be displayed'
        savefig("%s%s%s.%s" % (self._plotpath,self.name,self.suffix,self._format))

class centered_envelope(object):
    """
    E = centered_envelope(sorted_func_stack, mass)

    An object corresponding to the centered CI envelope 
    of a function enclosing a particular probability mass.

    :Arguments:
        sorted_func_stack: The samples of the function, sorted. 
            if func_stacks[i,:] gives sample i, then 
            sorted_func_stack is sort(func_stacks,0).

        mass: The probability mass enclosed by the CI envelope.

    :SeeAlso: func_envelopes
    """
    def __init__(self, sorted_func_stack, mass):
        if mass<0 or mass>1:
            raise ValueError, 'mass must be between 0 and 1'
        N_samp = shape(sorted_func_stack)[0]
        self.mass = mass
        self.ndim = len(sorted_func_stack.shape)-1

        if self.mass == 0:
            self.value = sorted_func_stack[int(N_samp*.5),]
        else:
            quandiff = .5*(1.-self.mass)
            self.lo = sorted_func_stack[int(N_samp*quandiff),]
            self.hi = sorted_func_stack[int(N_samp*(1.-quandiff)),]

    def display(self, xaxis, alpha, new=True):
        """
        E.display(xaxis, alpha = .8)

        :Arguments: xaxis, alpha

        Plots the CI region on the current figure, with respect to
        xaxis, at opacity alpha.

        :Note: The fill color of the envelope will be self.mass
            on the grayscale.
        """
        if new:
            figure()
        if self.ndim == 1:
            if self.mass>0.:
                x = concatenate((xaxis,xaxis[::-1]))
                y = concatenate((self.lo, self.hi[::-1]))
                fill(x,y,facecolor='%f' % self.mass,alpha=alpha, label = ('centered CI ' + str(self.mass)))
            else:
                pyplot(xaxis,self.value,'k-',alpha=alpha, label = ('median'))
        else:
            if self.mass>0.:
                subplot(1,2,1)
                contourf(xaxis[0],xaxis[1],self.lo,cmap=cm.bone)
                colorbar()
                subplot(1,2,2)
                contourf(xaxis[0],xaxis[1],self.hi,cmap=cm.bone)
                colorbar()
            else:
                contourf(xaxis[0],xaxis[1],self.value,cmap=cm.bone)
                colorbar()


def plotwrapper(f):
    """
    This decorator allows for PyMC arguments of various types to be passed to
    the plotting functions. It identifies the type of object and locates its 
    trace(s), then passes the data to the wrapped plotting function.
    
    """
    
    def wrapper(pymc_obj, *args, **kwargs):
        
        start = 0
        if kwargs.has_key('start'):
            start = kwargs.pop('start')
    
        # Figure out what type of object it is
        try:
            # First try Model type
            for variable in pymc_obj._variables_to_tally:            
                # Plot object
                if variable._plot:
                    data = variable.trace()[start:]
                    name = variable.__name__
                    f(data, name, *args, **kwargs)
            return
        except AttributeError:
            pass
            
        try:
            # Then try Node type
            if pymc_obj._plot:
                data = pymc_obj.trace()[start:]
                name = pymc_obj.__name__
                f(data, name, *args, **kwargs)
            return
        except AttributeError:
            pass
            
        # If others fail, assume that raw data is passed
        f(pymc_obj, *args, **kwargs)
    
    return wrapper


@plotwrapper
def plot(data, name, format='png', suffix='', path='./', new=True, last=True, rows=1, num=1, fontmap = {1:10, 2:8, 3:6, 4:5, 5:4}, verbose=1):
    """
    Generates summary plots for nodes of a given PyMC object.
    
    :Arguments:
        data: array or list
            A trace from an MCMC sample.
            
        name: string
            The name of the object.
        
        format (optional): string
            Graphic output format (defaults to png).
            
        suffix (optional): string
            Filename suffix.
        
        path (optional): string
            Specifies location for saving plots (defaults to local directory).
            
    """
        
    # If there is only one data array, go ahead and plot it ...
    if rank(data)==1:
        
        if verbose>0:
            print 'Plotting', name
        
        # If new plot, generate new frame
        if new:
            
            figure(figsize=(10, 6))
        
        # Call trace
        trace(data, name, rows=rows, columns=2, num=num, last=last)
        # Call histogram
        histogram(data, name, rows=rows, columns=2, num=num+1, last=last)
        
        if last:
            if not os.path.exists(path):
                os.mkdir(path)
                
            savefig("%s%s%s.%s" % (path, name, suffix, format))
    
    else:
        # ... otherwise plot recursively
        tdata = swapaxes(data, 0, 1)
        
        # How many rows?
        _rows = min(4, len(tdata))
        
        for i in range(len(tdata)):
            
            # New plot or adding to existing?
            _new = not i % _rows
            # Current subplot number
            _num = i % _rows * 2 + 1
            # Final subplot of current figure?
            _last = not (_num + 1) % (_rows * 2)
            
            plot(tdata[i], name+'_'+str(i), format=format, suffix=suffix, new=_new, last=_last, rows=_rows, num=_num)


@plotwrapper
def histogram(data, name, nbins=None, format='png', suffix='', path='./', rows=1, columns=1, num=1, last=True, fontmap = {1:10, 2:8, 3:6, 4:5, 5:4}, verbose=1):

    # Internal histogram specification for handling nested arrays
    try:
        
        # Stand-alone plot or subplot?
        standalone = rows==1 and columns==1 and num==1
        if standalone:
            if verbose>0:
                print 'Generating histogram of', name
            figure()
        
        subplot(rows, columns, num)
        
        #Specify number of bins (10 as default)
        nbins = nbins or int(4 + 1.5*log(len(data)))
        
        # Generate histogram
        hist(data.tolist(), nbins)
        
        # Plot options
        if last:
            xlabel(name, fontsize='x-small')
        
        ylabel("Frequency", fontsize='x-small')
        
        # Smaller tick labels
        tlabels = gca().get_xticklabels()
        setp(tlabels, 'fontsize', fontmap[rows])
        tlabels = gca().get_yticklabels()
        setp(tlabels, 'fontsize', fontmap[rows])
        
        if standalone:
            if not os.path.exists(path):
                os.mkdir(path)
            # Save to file
            savefig("%s%s%s.%s" % (path, name, suffix, format))
            #close()
    
    except OverflowError:
        print '... cannot generate histogram'


@plotwrapper
def trace(data, name, format='png', suffix='', path='./', rows=1, columns=1, num=1, last=True, fontmap = {1:10, 2:8, 3:6, 4:5, 5:4}, verbose=1):
    # Internal plotting specification for handling nested arrays
    
    # Stand-alone plot or subplot?
    standalone = rows==1 and columns==1 and num==1
    
    if standalone:
        if verbose>0:
            print 'Plotting', name
        figure()
    
    subplot(rows, columns, num)
    pyplot(data.tolist())
    
    # Plot options
    if last:
        xlabel('Iteration', fontsize='x-small')
    ylabel(name, fontsize='x-small')
    
    # Smaller tick labels
    tlabels = gca().get_xticklabels()
    setp(tlabels, 'fontsize', fontmap[rows])
    
    tlabels = gca().get_yticklabels()
    setp(tlabels, 'fontsize', fontmap[rows])
    
    if standalone:
        if not os.path.exists(path):
            os.mkdir(path)
        # Save to file
        savefig("%s%s%s.%s" % (path, name, suffix, format))
        #close()

@plotwrapper
def geweke_plot(data, name, format='png', suffix='-diagnostic', path='./', fontmap = {1:10, 2:8, 3:6, 4:5, 5:4}, verbose=1):
    
    # Generate Geweke (1992) diagnostic plots
    
    # print 'Plotting', name+suffix
    
    # Generate new scatter plot
    figure()
    x, y = transpose(data)
    scatter(x.tolist(), y.tolist())
    
    # Plot options
    xlabel('First iteration', fontsize='x-small')
    ylabel('Z-score', fontsize='x-small')
    
    # Plot lines at +/- 2 sd from zero
    pyplot((min(x), max(x)), (2, 2), '--')
    pyplot((min(x), max(x)), (-2, -2), '--')
    
    # Set plot bound
    ylim(min(-2.5, min(y)), max(2.5, max(y)))
    xlim(0, max(x))
    
    # Save to file
    if not os.path.exists(path):
        os.mkdir(path)
    savefig("%s%s%s.%s" % (path, name, suffix, format))
    #close()

@plotwrapper
def gof_plot(data, name, format='png', suffix='-gof', path='./', fontmap = {1:10, 2:8, 3:6, 4:5, 5:4}, verbose=1):
    # Generate goodness-of-fit scatter plot
    if verbose>0:
        print 'Plotting', name+suffix
    
    # Generate new scatter plot
    figure()
    x, y = data
    scatter(x, y)
    
    # Plot x=y line
    lo = min(ravel(data))
    hi = max(ravel(data))
    datarange = hi-lo
    lo -= 0.1*datarange
    hi += 0.1*datarange
    pyplot((lo, hi), (lo, hi))
    
    # Plot options
    xlabel('Observed deviates', fontsize='x-small')
    ylabel('Simulated deviates', fontsize='x-small')
    
    # Save to file
    if not os.path.exists(path):
        os.mkdir(path)
    savefig("%s%s%s.%s" % (path, name, suffix, format))
    #close()

def bar_series_plot(values, ylab='Y', format='png', suffix='', path='./', fontmap = {1:10, 2:8, 3:6, 4:5, 5:4}, verbose=1):
    
    """Generate bar plot of a series, usually autocorrelation
    or autocovariance."""
    
    # Extract names
    names = values.keys()
    names.sort()
    
    # Number of plots per page
    rows = min(len(values), 4)
    
    for i,name in enumerate(names):
        if verbose>0:
            print 'Plotting', name+suffix
        
        if not i % rows:
             # Generate new figure
            figure(figsize=(10, 6))
        
        # New subplot
        subplot(rows, 1, i - (rows*(i/rows)) + 1)
        y = values[name]
        x = arange(len(y))
        bar(x, y)
        
        # Set axis bounds
        ylim(-1.0, 1.0)
        xlim(0, len(y))
        
        # Plot options
        ylabel(ylab, fontsize='x-small')
        tlabels = gca().get_yticklabels()
        setp(tlabels, 'fontsize', fontmap[rows])
        tlabels = gca().get_xticklabels()
        setp(tlabels, 'fontsize', fontmap[rows])
        
        # Save to file
        if not (i+1) % rows or i == len(values)-1:
            
            # Label X-axis on last subplot
            xlabel('Lag', fontsize='x-small')
            
            if not os.path.exists(path):
                os.mkdir(path)
            savefig("%s%s%s.%s" % (path, name, suffix, format))
            #close()

# TODO: make sure pair_posterior works.
def pair_posterior(nodes, mask=None, trueval=None, fontsize=8, suffix='', new=True, fontmap = {1:10, 2:8, 3:6, 4:5, 5:4}, verbose=1):
    """
    pair_posterior(nodes, clear=True, mask=None, trueval=None)

    :Arguments:
    nodes:       An iterable containing stochastic objects with traces.
    mask:       A dictionary, indexed by stochastic, of boolean-valued
                arrays. If mask[p][index]=False, stochastic p's value
                at that index will be included in the plot.
    trueval:    The true values of stochastics (useful for summarizing
                performance with simulated data).

    Produces a matrix of plots. On the diagonals are the marginal
    posteriors of the stochastics, subject to the masks. On the
    off-diagonals are the marginal pairwise posteriors of the
    stochastics, subject to the masks.
    """

    nodes = list(nodes)

    if mask is not None:
        mask={}
        for p in nodes:
            mask[p] = None

    if trueval is not None:
        trueval={}
        for p in nodes:
            trueval[p] = None

    np=len(nodes)
    ns = {}
    for p in nodes:
        if not p.value.shape:
            ns[p] = 1
        else:
            ns[p] = len(p.value.ravel())

    index_now = -1
    tracelen = {}
    ravelledtrace={}
    titles={}
    indices={}
    cum_indices={}


    for p in nodes:

        tracelen[p] = p.trace().shape[0]
        ravelledtrace[p] = p.trace().reshape((tracelen[p],-1))
        titles[p]=[]
        indices[p] = []
        cum_indices[p]=[]

        for j in range(ns[p]):
            # Should this index be included?
            if mask[p]:
                if not mask[p].ravel()[j]:
                    indices[p].append(j)
                    this_index=True
                else:
                    this_index=False
            else:
                indices[p].append(j)
                this_index=True
            # If so:
            if this_index:
                index_now+=1
                cum_indices[p].append(index_now)
                # Figure out title string
                if ns[p]==1:
                    titles[p].append(p.__name__)
                else:
                    titles[p].append(p.__name__ + get_index_list(p.value.shape,j).__repr__())

    if new:
        figure(figsize = (10,10))

    n = index_now+1
    for p in nodes:
        for j in range(len(indices[p])):
            # Marginals
            ax=subplot(n,n,(cum_indices[p][j])*(n+1)+1)
            setp(ax.get_xticklabels(),fontsize=fontsize)
            setp(ax.get_yticklabels(),fontsize=fontsize)
            hist(ravelledtrace[p][:,j],normed=True,fill=False)
            xlabel(titles[p][j],size=fontsize)

    # Bivariates
    for i in range(len(nodes)-1):
        p0 = nodes[i]
        for j in range(len(indices[p0])):
            p0_i = indices[p0][j]
            p0_ci = cum_indices[p0][j]
            for k in range(i,len(nodes)):
                p1=nodes[k]
                if i==k:
                    l_range = range(j+1,len(indices[p0]))
                else:
                    l_range = range(len(indices[p1]))
                for l  in l_range:
                    p1_i = indices[p1][l]
                    p1_ci = cum_indices[p1][l]
                    subplot_index = p0_ci*(n) + p1_ci+1
                    ax=subplot(n, n, subplot_index)
                    setp(ax.get_xticklabels(),fontsize=fontsize)
                    setp(ax.get_yticklabels(),fontsize=fontsize)

                    try:
                        H, x, y = histogram2d(ravelledtrace[p1][:,p1_i],ravelledtrace[p0][:,p0_i])
                        contourf(x,y,H,cmap=cm.bone)
                    except:
                        print 'Unable to plot histogram for ('+titles[p1][l]+','+titles[p0][j]+'):'
                        pyplot(ravelledtrace[p1][:,p1_i],ravelledtrace[p0][:,p0_i],'k.',markersize=1.)
                        axis('tight')

                    xlabel(titles[p1][l],size=fontsize)
                    ylabel(titles[p0][j],size=fontsize)

    plotname = ''
    for obj in nodes:
        plotname += obj.__name__ + ''
    if not os.path.exists(path):
        os.mkdir(path)
    savefig("%s%s%s.%s" % (path, plotname, suffix, format))

